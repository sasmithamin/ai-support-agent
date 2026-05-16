"""
CRUD operations for database models
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from datetime import datetime

from src.db.models import Ticket, Conversation, KnowledgeDocument, TicketStatus


async def create_ticket(
    session: AsyncSession,
    user_id: str,
    subject: str,
    description: str,
    user_email: Optional[str] = None,
    category: str = "general",
    sentiment_score: Optional[float] = None,
    confidence_score: Optional[float] = None
) -> Ticket:
    """Create a new support ticket"""
    
    # Generate ticket number
    result = await session.execute(select(func.count(Ticket.id)))
    count = result.scalar() or 0
    ticket_number = f"TKT-{count + 1:05d}"
    
    ticket = Ticket(
        ticket_number=ticket_number,
        user_id=user_id,
        user_email=user_email,
        subject=subject,
        description=description,
        category=category,
        sentiment_score=sentiment_score,
        confidence_score=confidence_score
    )
    
    session.add(ticket)
    await session.commit()
    await session.refresh(ticket)
    
    return ticket


async def get_ticket(session: AsyncSession, ticket_id: int) -> Optional[Ticket]:
    """Get a ticket by ID"""
    result = await session.execute(
        select(Ticket).where(Ticket.id == ticket_id)
    )
    return result.scalar_one_or_none()


async def get_ticket_by_number(session: AsyncSession, ticket_number: str) -> Optional[Ticket]:
    """Get a ticket by ticket number"""
    result = await session.execute(
        select(Ticket).where(Ticket.ticket_number == ticket_number)
    )
    return result.scalar_one_or_none()


async def get_user_tickets(
    session: AsyncSession,
    user_id: str,
    limit: int = 10
) -> List[Ticket]:
    """Get all tickets for a user"""
    result = await session.execute(
        select(Ticket)
        .where(Ticket.user_id == user_id)
        .order_by(desc(Ticket.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def update_ticket_status(
    session: AsyncSession,
    ticket_id: int,
    status: TicketStatus,
    resolution: Optional[str] = None
) -> Optional[Ticket]:
    """Update ticket status"""
    ticket = await get_ticket(session, ticket_id)
    if not ticket:
        return None
    
    ticket.status = status
    if resolution:
        ticket.resolution = resolution
    
    if status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.utcnow()
    
    ticket.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(ticket)
    
    return ticket


async def add_conversation(
    session: AsyncSession,
    ticket_id: int,
    role: str,
    content: str,
    tokens_used: Optional[int] = None,
    tool_calls: Optional[str] = None
) -> Conversation:
    """Add a conversation message"""
    conversation = Conversation(
        ticket_id=ticket_id,
        role=role,
        content=content,
        tokens_used=tokens_used,
        tool_calls=tool_calls
    )
    
    session.add(conversation)
    await session.commit()
    await session.refresh(conversation)
    
    return conversation


async def get_ticket_conversations(
    session: AsyncSession,
    ticket_id: int
) -> List[Conversation]:
    """Get all conversations for a ticket"""
    result = await session.execute(
        select(Conversation)
        .where(Conversation.ticket_id == ticket_id)
        .order_by(Conversation.timestamp)
    )
    return list(result.scalars().all())


async def get_open_tickets(
    session: AsyncSession,
    limit: int = 50
) -> List[Ticket]:
    """Get all open tickets"""
    result = await session.execute(
        select(Ticket)
        .where(Ticket.status.in_([TicketStatus.OPEN, TicketStatus.IN_PROGRESS]))
        .order_by(desc(Ticket.created_at))
        .limit(limit)
    )
    return list(result.scalars().all())


async def get_ticket_stats(session: AsyncSession) -> dict:
    """Get ticket statistics"""
    
    # Total tickets
    total_result = await session.execute(select(func.count(Ticket.id)))
    total = total_result.scalar() or 0
    
    # Open tickets
    open_result = await session.execute(
        select(func.count(Ticket.id))
        .where(Ticket.status == TicketStatus.OPEN)
    )
    open_count = open_result.scalar() or 0
    
    # Resolved tickets
    resolved_result = await session.execute(
        select(func.count(Ticket.id))
        .where(Ticket.status == TicketStatus.RESOLVED)
    )
    resolved_count = resolved_result.scalar() or 0
    
    # Average sentiment
    sentiment_result = await session.execute(
        select(func.avg(Ticket.sentiment_score))
        .where(Ticket.sentiment_score.isnot(None))
    )
    avg_sentiment = sentiment_result.scalar() or 0.0
    
    return {
        "total_tickets": total,
        "open_tickets": open_count,
        "resolved_tickets": resolved_count,
        "average_sentiment": float(avg_sentiment)
    }