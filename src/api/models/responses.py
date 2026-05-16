"""
Pydantic response models for API
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class SentimentResponse(BaseModel):
    """Sentiment analysis response"""
    sentiment: str
    score: float
    urgency: str
    emotion: str


class EscalationResponse(BaseModel):
    """Escalation decision response"""
    should_escalate: bool
    reason: str
    priority: str
    suggested_team: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Agent's response")
    ticket_id: Optional[int] = Field(None, description="Associated ticket ID")
    sentiment: SentimentResponse
    confidence: float = Field(..., ge=0.0, le=1.0)
    escalation: EscalationResponse
    tools_used: List[str] = Field(default_factory=list)
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "I can help you reset your password! Here's how...",
                "ticket_id": 1,
                "sentiment": {
                    "sentiment": "neutral",
                    "score": 0.1,
                    "urgency": "medium",
                    "emotion": "confused"
                },
                "confidence": 0.85,
                "escalation": {
                    "should_escalate": False,
                    "reason": "AI can handle this",
                    "priority": "medium"
                },
                "tools_used": ["knowledge_search"]
            }
        }


class TicketResponse(BaseModel):
    """Response model for ticket"""
    id: int
    ticket_number: str
    user_id: str
    subject: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Response model for conversation message"""
    id: int
    ticket_id: int
    role: str
    content: str
    timestamp: datetime
    
    class Config:
        from_attributes = True


class StatsResponse(BaseModel):
    """Response model for statistics"""
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    average_sentiment: float
    vector_store_documents: int
    registered_tools: int


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)