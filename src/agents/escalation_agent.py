"""
Escalation decision agent for determining when to route to humans
"""
from typing import Dict, Any, Optional
import logging
import json

from src.utils.llm_factory import get_llm
from src.utils.prompt_templates import ESCALATION_DECISION_PROMPT
from config.settings import settings

logger = logging.getLogger(__name__)


class EscalationAgent:
    """Decides when tickets should be escalated to human agents"""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.2)
        self.escalation_threshold = settings.auto_escalation_threshold
    
    def should_escalate(
        self,
        subject: str,
        description: str,
        conversation_history: str,
        status: str,
        confidence: float,
        sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Determine if a ticket should be escalated
        
        Args:
            subject: Ticket subject
            description: Ticket description
            conversation_history: Full conversation text
            status: Current ticket status
            confidence: AI confidence score (0-1)
            sentiment: Sentiment analysis results
            
        Returns:
            Dictionary with escalation decision and details
        """
        try:
            logger.info(f"Evaluating escalation (confidence: {confidence:.2f})")
            
            # Quick checks for automatic escalation
            if confidence < self.escalation_threshold:
                return self._escalate("Low AI confidence", "high", "technical")
            
            if sentiment.get("score", 0) < -0.5:
                return self._escalate("Customer highly frustrated", "urgent", "general")
            
            # Keywords that trigger immediate escalation
            escalation_keywords = [
                "legal", "lawsuit", "lawyer", "attorney",
                "refund", "charge back", "billing issue",
                "account locked", "security breach", "hacked",
                "cancel subscription", "cancel account"
            ]
            
            text_lower = f"{subject} {description}".lower()
            for keyword in escalation_keywords:
                if keyword in text_lower:
                    return self._escalate(
                        f"Critical keyword detected: {keyword}",
                        "urgent",
                        "billing" if keyword in ["refund", "charge back", "billing"] else "technical"
                    )
            
            # Use LLM for nuanced decision
            prompt = ESCALATION_DECISION_PROMPT.format(
                subject=subject,
                description=description,
                conversation=conversation_history,
                status=status,
                confidence=confidence,
                sentiment=sentiment.get("sentiment", "neutral")
            )
            
            response = self.llm.invoke(prompt)
            
            # Parse response
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            response_text = response_text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            result = json.loads(response_text.strip())
            
            logger.info(f"Escalation decision: {result.get('should_escalate')}")
            
            return {
                "should_escalate": result.get("should_escalate", False),
                "reason": result.get("reason", ""),
                "priority": result.get("priority", "medium"),
                "suggested_team": result.get("suggested_team", "general")
            }
            
        except Exception as e:
            logger.error(f"Escalation evaluation error: {e}")
            # On error, err on the side of caution - don't escalate
            return {
                "should_escalate": False,
                "reason": "Error in escalation analysis",
                "priority": "medium",
                "suggested_team": "general"
            }
    
    def _escalate(self, reason: str, priority: str, team: str) -> Dict[str, Any]:
        """Helper to create escalation decision"""
        return {
            "should_escalate": True,
            "reason": reason,
            "priority": priority,
            "suggested_team": team
        }


# Global instance
_escalation_agent = None


def get_escalation_agent() -> EscalationAgent:
    """Get or create the global escalation agent"""
    global _escalation_agent
    if _escalation_agent is None:
        _escalation_agent = EscalationAgent()
    return _escalation_agent