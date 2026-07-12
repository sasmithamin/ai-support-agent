"""
Main support agent for handling customer queries
"""
from typing import Dict, Any, List, Optional
import logging

from src.utils.llm_factory import get_llm
from src.utils.prompt_templates import SUPPORT_AGENT_SYSTEM_PROMPT
from src.mcp.server import get_mcp_server
from src.agents.sentiment_agent import get_sentiment_agent
from src.agents.escalation_agent import get_escalation_agent
from config.settings import settings

logger = logging.getLogger(__name__)


class SupportAgent:
    """Main AI support agent for customer interactions"""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.7)
        self.mcp_server = get_mcp_server()
        self.sentiment_agent = get_sentiment_agent()
        self.escalation_agent = get_escalation_agent()
        self.conversation_history: List[Dict[str, str]] = []
        self.tools = self.mcp_server.tools_registry.get_all_tools()
        
        logger.info(f"Support agent initialized with {len(self.tools)} tools")
    
    def process_message(
        self,
        user_message: str,
        user_id: Optional[str] = None,
        ticket_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process a customer message and generate response
        """
        try:
            logger.info(f"Processing message: '{user_message[:50]}...'")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Analyze sentiment
            sentiment_result = self.sentiment_agent.analyze(user_message)
            logger.info(f"Sentiment: {sentiment_result['sentiment']} ({sentiment_result['score']:.2f})")
            
            # Get conversation context
            context = self._format_conversation_history()
            
            # Build prompt
            prompt = SUPPORT_AGENT_SYSTEM_PROMPT.format(
                context=context,
                query=user_message
            )
            
            # Execute agent
            agent_response = self._execute_agent(prompt)
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            # Calculate confidence
            confidence = self._calculate_confidence(agent_response, sentiment_result)
            
            # Check escalation
            escalation_result = self.escalation_agent.should_escalate(
                subject=user_message[:100],
                description=user_message,
                conversation_history=context,
                status="open",
                confidence=confidence,
                sentiment=sentiment_result
            )
            
            return {
                "response": agent_response,
                "sentiment": sentiment_result,
                "confidence": confidence,
                "escalation": escalation_result,
                "tools_used": self._extract_tools_used(agent_response)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {
                "response": (
                    "I apologize, but I encountered an error. "
                    "Let me connect you with a human agent."
                ),
                "sentiment": {"sentiment": "neutral", "score": 0.0,
                             "urgency": "medium", "emotion": "neutral",
                             "escalation_recommended": False},
                "confidence": 0.0,
                "escalation": {
                    "should_escalate": True,
                    "reason": "System error",
                    "priority": "high",
                    "suggested_team": "technical"
                },
                "tools_used": []
            }
    
    def _execute_agent(self, prompt: str) -> str:
        """Execute agent with tools"""
        try:
            # Search knowledge base for relevant info
            knowledge_result = None
            keywords = ['how', 'what', 'where', 'when', 'why',
                       'help', 'issue', 'problem', 'error', 'cant',
                       "can't", 'not working', 'failed']
            
            if any(kw in prompt.lower() for kw in keywords):
                try:
                    from src.tools.knowledge_search import get_knowledge_search_tool
                    knowledge_tool = get_knowledge_search_tool()
                    knowledge_result = knowledge_tool.run(prompt)
                    logger.info("Knowledge search executed")
                except Exception as e:
                    logger.warning(f"Knowledge search failed: {e}")
            
            # Build enhanced prompt
            enhanced_prompt = prompt
            if knowledge_result and "No relevant information" not in knowledge_result:
                enhanced_prompt += f"\n\nKnowledge Base Results:\n{knowledge_result}"
            
            # Generate response
            response = self.llm.invoke(enhanced_prompt)
            
            if hasattr(response, 'content'):
                return response.content
            return str(response)
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return (
                "I'm having trouble processing your request. "
                "Could you rephrase, or would you like to speak with a human agent?"
            )
    
    def _format_conversation_history(self, max_messages: int = 10) -> str:
        """Format conversation history for context"""
        recent = self.conversation_history[-max_messages:]
        formatted = []
        for msg in recent:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted) if formatted else "No previous conversation"
    
    def _calculate_confidence(
        self,
        response: str,
        sentiment: Dict[str, Any]
    ) -> float:
        """Calculate confidence score"""
        confidence = 0.7
        
        if len(response) < 50:
            confidence -= 0.2
        
        uncertainty_phrases = [
            "i'm not sure", "i don't know", "unclear",
            "uncertain", "might be", "possibly", "perhaps", "maybe"
        ]
        if any(phrase in response.lower() for phrase in uncertainty_phrases):
            confidence -= 0.3
        
        if len(response) > 200:
            confidence += 0.1
        
        if sentiment.get("score", 0) < -0.3:
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_tools_used(self, response: str) -> List[str]:
        """Extract which tools were used"""
        tools_used = []
        if "knowledge base" in response.lower():
            tools_used.append("knowledge_search")
        if "searched" in response.lower():
            tools_used.append("web_search")
        return tools_used
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")


# Global instance
_support_agent = None


def get_support_agent() -> SupportAgent:
    """Get or create the global support agent"""
    global _support_agent
    if _support_agent is None:
        _support_agent = SupportAgent()
    return _support_agent