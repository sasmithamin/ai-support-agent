"""
Ticket management tool for creating and updating support tickets
"""
from typing import Optional
from langchain.tools import BaseTool
from pydantic import Field
import logging
from datetime import datetime
import json

from src.db.models import Ticket, TicketStatus, TicketPriority
from src.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class TicketManagerTool(BaseTool):
    """Tool for managing support tickets"""
    
    name: str = "ticket_manager"
    description: str = (
        "Create or update support tickets. Use this to: "
        "1. Create a new ticket for the customer's issue "
        "2. Update ticket status (open, in_progress, resolved, escalated) "
        "3. Update ticket priority (low, medium, high, urgent) "
        "4. Add resolution notes "
        "Input should be a JSON string with fields: "
        "action (create/update), ticket_id (for updates), "
        "subject, description, status, priority, resolution"
    )
    
    def _run(self, action_json: str) -> str:
        """
        Execute ticket management action
        
        Args:
            action_json: JSON string with action details
            
        Returns:
            Result message
        """
        try:
            # Parse input
            action = json.loads(action_json)
            action_type = action.get('action', 'create')
            
            if action_type == 'create':
                return self._create_ticket(action)
            elif action_type == 'update':
                return self._update_ticket(action)
            else:
                return f"Unknown action: {action_type}. Use 'create' or 'update'"
                
        except json.JSONDecodeError:
            return "Invalid JSON input. Please provide valid JSON."
        except Exception as e:
            logger.error(f"Ticket manager error: {e}")
            return f"Error managing ticket: {str(e)}"
    
    def _create_ticket(self, data: dict) -> str:
        """Create a new ticket"""
        try:
            import asyncio
            return asyncio.run(self._create_ticket_async(data))
        except Exception as e:
            logger.error(f"Error creating ticket: {e}")
            return f"Error creating ticket: {str(e)}"
    
    async def _create_ticket_async(self, data: dict) -> str:
        """Async ticket creation"""
        async with AsyncSessionLocal() as session:
            # Generate ticket number
            from sqlalchemy import select, func
            result = await session.execute(
                select(func.count(Ticket.id))
            )
            count = result.scalar() or 0
            ticket_number = f"TKT-{count + 1:05d}"
            
            # Create ticket
            ticket = Ticket(
                ticket_number=ticket_number,
                user_id=data.get('user_id', 'unknown'),
                user_email=data.get('user_email'),
                subject=data.get('subject', 'No subject'),
                description=data.get('description', ''),
                category=data.get('category', 'general'),
                status=TicketStatus.OPEN,
                priority=TicketPriority(data.get('priority', 'medium')),
                sentiment_score=data.get('sentiment_score'),
                confidence_score=data.get('confidence_score')
            )
            
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
            
            logger.info(f"Created ticket {ticket_number}")
            
            return (
                f"Successfully created ticket {ticket_number}\n"
                f"Subject: {ticket.subject}\n"
                f"Status: {ticket.status.value}\n"
                f"Priority: {ticket.priority.value}"
            )
    
    def _update_ticket(self, data: dict) -> str:
        """Update an existing ticket"""
        try:
            import asyncio
            return asyncio.run(self._update_ticket_async(data))
        except Exception as e:
            logger.error(f"Error updating ticket: {e}")
            return f"Error updating ticket: {str(e)}"
    
    async def _update_ticket_async(self, data: dict) -> str:
        """Async ticket update"""
        from sqlalchemy import select
        
        ticket_id = data.get('ticket_id')
        if not ticket_id:
            return "ticket_id is required for updates"
        
        async with AsyncSessionLocal() as session:
            # Get ticket
            result = await session.execute(
                select(Ticket).where(Ticket.id == ticket_id)
            )
            ticket = result.scalar_one_or_none()
            
            if not ticket:
                return f"Ticket {ticket_id} not found"
            
            # Update fields
            if 'status' in data:
                ticket.status = TicketStatus(data['status'])
            if 'priority' in data:
                ticket.priority = TicketPriority(data['priority'])
            if 'resolution' in data:
                ticket.resolution = data['resolution']
                if data['status'] == 'resolved':
                    ticket.resolved_at = datetime.utcnow()
                    ticket.auto_resolved = data.get('auto_resolved', False)
            if 'assigned_to' in data:
                ticket.assigned_to = data['assigned_to']
            if 'escalated' in data:
                ticket.escalated = data['escalated']
            
            ticket.updated_at = datetime.utcnow()
            
            await session.commit()
            
            logger.info(f"Updated ticket {ticket.ticket_number}")
            
            return (
                f"Successfully updated ticket {ticket.ticket_number}\n"
                f"Status: {ticket.status.value}\n"
                f"Priority: {ticket.priority.value}"
            )
    
    async def _arun(self, action_json: str) -> str:
        """Async version"""
        return self._run(action_json)


def get_ticket_manager_tool() -> TicketManagerTool:
    """Get ticket manager tool instance"""
    return TicketManagerTool()