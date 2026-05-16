"""
Main support agent for handling customer queries
"""
from typing import Dict, Any, List, Optional
import logging
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

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
        
        # Get tools from MCP server
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
        
        Args:
            user_message: Customer's message
            user_id: Optional user identifier
            ticket_id: Optional existing ticket ID
            
        Returns:
            Dictionary with response and metadata
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
            
            # Create agent with tools
            agent_response = self._execute_agent(prompt)
            
            # Add response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": agent_response
            })
            
            # Calculate confidence (simplified - based on response length and keywords)
            confidence = self._calculate_confidence(agent_response, sentiment_result)
            
            # Check if escalation needed
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
                    "I apologize, but I encountered an error processing your request. "
                    "Let me connect you with a human agent who can help you better."
                ),
                "sentiment": {"sentiment": "neutral", "score": 0.0},
                "confidence": 0.0,
                "escalation": {
                    "should_escalate": True,
                    "reason": "System error",
                    "priority": "high"
                },
                "tools_used": []
            }
    
    def _execute_agent(self, prompt: str) -> str:
        """
        Execute agent with tools
        
        Args:
            prompt: Formatted prompt with context
            
        Returns:
            Agent response
        """
        try:
            # For simplicity, we'll use a basic approach
            # In production, you'd use LangChain's AgentExecutor with ReAct pattern
            
            # First, try to search knowledge base
            knowledge_search_result = None
            if any(keyword in prompt.lower() for keyword in ['how', 'what', 'where', 'when', 'why', 'help', 'issue', 'problem']):
                try:
                    from src.tools.knowledge_search import get_knowledge_search_tool
                    knowledge_tool = get_knowledge_search_tool()
                    knowledge_search_result = knowledge_tool.run(prompt)
                    logger.info("Knowledge search executed")
                except Exception as e:
                    logger.warning(f"Knowledge search failed: {e}")
            
            # Build enhanced prompt with knowledge if found
            enhanced_prompt = prompt
            if knowledge_search_result and "No relevant information found" not in knowledge_search_result:
                enhanced_prompt += f"\n\nKnowledge Base Search Results:\n{knowledge_search_result}"
            
            # Generate response using LLM
            response = self.llm.invoke(enhanced_prompt)
            
            if hasattr(response, 'content'):
                return response.content
            return str(response)
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return (
                "I'm having trouble processing your request right now. "
                "Could you please rephrase your question, or would you like me "
                "to connect you with a human agent?"
            )
    
    def _format_conversation_history(self, max_messages: int = 10) -> str:
        """Format conversation history for context"""
        recent_history = self.conversation_history[-max_messages:]
        
        formatted = []
        for msg in recent_history:
            role = "Customer" if msg["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {msg['content']}")
        
        return "\n".join(formatted) if formatted else "No previous conversation"
    
    def _calculate_confidence(
        self,
        response: str,
        sentiment: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence score for the response
        
        Args:
            response: Agent's response
            sentiment: Sentiment analysis result
            
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.7  # Base confidence
        
        # Lower confidence if response is too short
        if len(response) < 50:
            confidence -= 0.2
        
        # Lower confidence if response contains uncertainty phrases
        uncertainty_phrases = [
            "i'm not sure", "i don't know", "unclear", "uncertain",
            "might be", "possibly", "perhaps", "maybe"
        ]
        if any(phrase in response.lower() for phrase in uncertainty_phrases):
            confidence -= 0.3
        
        # Higher confidence if response is detailed
        if len(response) > 200:
            confidence += 0.1
        
        # Adjust based on sentiment
        if sentiment.get("score", 0) < -0.3:
            confidence -= 0.1  # Lower confidence for negative sentiment
        
        return max(0.0, min(1.0, confidence))
    
    def _extract_tools_used(self, response: str) -> List[str]:
        """Extract which tools were used (simplified)"""
        tools_used = []
        
        if "knowledge base" in response.lower() or "documentation" in response.lower():
            tools_used.append("knowledge_search")
        
        if "searched" in response.lower() or "found online" in response.lower():
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