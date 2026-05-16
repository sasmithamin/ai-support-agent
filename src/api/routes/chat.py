"""
Chat endpoints for customer support interactions
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.api.models.requests import ChatRequest
from src.api.models.responses import ChatResponse, ErrorResponse
from src.db.database import get_db
from src.db import crud
from src.agents.support_agent import get_support_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Chat with AI support agent
    
    - **message**: User's question or issue
    - **user_id**: Optional user identifier
    - **ticket_id**: Optional existing ticket ID
    """
    try:
        logger.info(f"Chat request from user: {request.user_id}")
        
        # Get support agent
        agent = get_support_agent()
        
        # Process message
        result = agent.process_message(
            user_message=request.message,
            user_id=request.user_id,
            ticket_id=request.ticket_id
        )
        
        # Create or update ticket
        ticket = None
        if request.ticket_id:
            # Get existing ticket
            ticket = await crud.get_ticket(db, request.ticket_id)
        else:
            # Create new ticket
            ticket = await crud.create_ticket(
                session=db,
                user_id=request.user_id or "anonymous",
                subject=request.message[:100],
                description=request.message,
                sentiment_score=result['sentiment']['score'],
                confidence_score=result['confidence']
            )
            logger.info(f"Created ticket: {ticket.ticket_number}")
        
        # Add conversation messages
        if ticket:
            # Add user message
            await crud.add_conversation(
                session=db,
                ticket_id=ticket.id,
                role="user",
                content=request.message
            )
            
            # Add agent response
            await crud.add_conversation(
                session=db,
                ticket_id=ticket.id,
                role="assistant",
                content=result['response']
            )
        
        # Update ticket if escalation needed
        if ticket and result['escalation']['should_escalate']:
            from src.db.models import TicketStatus
            ticket.escalated = True
            ticket.status = TicketStatus.ESCALATED
            await db.commit()
        
        return ChatResponse(
            response=result['response'],
            ticket_id=ticket.id if ticket else None,
            sentiment=result['sentiment'],
            confidence=result['confidence'],
            escalation=result['escalation'],
            tools_used=result['tools_used']
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )