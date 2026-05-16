"""
Sentiment analysis agent for detecting customer emotions
"""
from typing import Dict, Any
import logging
import json

from src.utils.llm_factory import get_llm
from src.utils.prompt_templates import SENTIMENT_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)


class SentimentAgent:
    """Analyzes customer sentiment and urgency"""
    
    def __init__(self):
        self.llm = get_llm(temperature=0.1)  # Low temperature for consistent analysis
    
    def analyze(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment of a customer message
        
        Args:
            message: Customer message text
            
        Returns:
            Dictionary with sentiment analysis results
        """
        try:
            logger.info("Analyzing sentiment...")
            
            # Format prompt
            prompt = SENTIMENT_ANALYSIS_PROMPT.format(message=message)
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Extract content
            if hasattr(response, 'content'):
                response_text = response.content
            else:
                response_text = str(response)
            
            # Parse JSON response
            # Remove markdown code blocks if present
            response_text = response_text.strip()
            if response_text.startswith('```'):
                response_text = response_text.split('```')[1]
                if response_text.startswith('json'):
                    response_text = response_text[4:]
            
            result = json.loads(response_text.strip())
            
            logger.info(f"Sentiment: {result.get('sentiment')}, Score: {result.get('score')}")
            
            return {
                "sentiment": result.get("sentiment", "neutral"),
                "score": float(result.get("score", 0.0)),
                "urgency": result.get("urgency", "medium"),
                "emotion": result.get("emotion", "neutral"),
                "escalation_recommended": result.get("escalation_recommended", False)
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse sentiment response: {e}")
            return self._default_sentiment()
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._default_sentiment()
    
    def _default_sentiment(self) -> Dict[str, Any]:
        """Return default neutral sentiment"""
        return {
            "sentiment": "neutral",
            "score": 0.0,
            "urgency": "medium",
            "emotion": "neutral",
            "escalation_recommended": False
        }
    
    def should_escalate(self, sentiment_result: Dict[str, Any]) -> bool:
        """
        Determine if ticket should be escalated based on sentiment
        
        Args:
            sentiment_result: Result from analyze()
            
        Returns:
            Boolean indicating if escalation is needed
        """
        score = sentiment_result.get("score", 0.0)
        urgency = sentiment_result.get("urgency", "medium")
        
        # Escalate if very negative or high urgency
        return (
            score < -0.5 or 
            urgency == "high" or 
            sentiment_result.get("escalation_recommended", False)
        )


# Global instance
_sentiment_agent = None


def get_sentiment_agent() -> SentimentAgent:
    """Get or create the global sentiment agent"""
    global _sentiment_agent
    if _sentiment_agent is None:
        _sentiment_agent = SentimentAgent()
    return _sentiment_agent