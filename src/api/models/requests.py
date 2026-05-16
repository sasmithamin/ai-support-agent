"""
Pydantic request models for API validation
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    user_id: Optional[str] = Field(None, description="User identifier")
    ticket_id: Optional[int] = Field(None, description="Existing ticket ID")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "I can't reset my password",
                "user_id": "user_123"
            }
        }


class TicketCreateRequest(BaseModel):
    """Request model for creating a ticket"""
    user_id: str = Field(..., description="User identifier")
    subject: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=5000)
    user_email: Optional[str] = Field(None, description="User email")
    category: str = Field("general", description="Ticket category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_123",
                "subject": "Login issue",
                "description": "I cannot log into my account",
                "user_email": "user@example.com"
            }
        }


class KnowledgeUploadRequest(BaseModel):
    """Request model for uploading knowledge documents"""
    title: str = Field(..., max_length=200)
    content: str = Field(..., min_length=10)
    category: str = Field("general")
    source: Optional[str] = Field(None, description="Source URL or file path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Password Reset Guide",
                "content": "To reset your password: 1. Go to login page...",
                "category": "authentication"
            }
        }