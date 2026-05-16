"""
Ticket management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from src.api.models.requests import TicketCreateRequest
from src.api.models.responses import TicketResponse, ConversationResponse
from src.db.database import get_db
from src.db import crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/", response_model=TicketResponse, status_code=201)
async def create_ticket(
    request: TicketCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new support ticket"""
    try:
        ticket = await crud.create_ticket(
            session=db,
            user_id=request.user_id,
            subject=request.subject,
            description=request.description,
            user_email=request.user_email,
            category=request.category
        )
        
        logger.info(f"Created ticket: {ticket.ticket_number}")
        return ticket
        
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{ticket_id}", response_model=TicketResponse)
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get ticket by ID"""
    ticket = await crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.get("/user/{user_id}", response_model=List[TicketResponse])
async def get_user_tickets(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all tickets for a user"""
    tickets = await crud.get_user_tickets(db, user_id, limit)
    return tickets


@router.get("/{ticket_id}/conversations", response_model=List[ConversationResponse])
async def get_ticket_conversations(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all conversations for a ticket"""
    # Check if ticket exists
    ticket = await crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    conversations = await crud.get_ticket_conversations(db, ticket_id)
    return conversations


@router.get("/", response_model=List[TicketResponse])
async def list_open_tickets(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get all open tickets"""
    tickets = await crud.get_open_tickets(db, limit)
    return tickets