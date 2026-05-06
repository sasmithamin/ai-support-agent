from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()


class TicketStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    user_email = Column(String)
    
    subject = Column(String)
    description = Column(Text)
    category = Column(String)
    
    status = Column(Enum(TicketStatus), default=TicketStatus.OPEN)
    priority = Column(Enum(TicketPriority), default=TicketPriority.MEDIUM)
    
    sentiment_score = Column(Float, nullable=True)  # -1 to 1
    confidence_score = Column(Float, nullable=True)  # 0 to 1
    
    assigned_to = Column(String, nullable=True)  # Human agent if escalated
    resolution = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    escalated = Column(Boolean, default=False)
    auto_resolved = Column(Boolean, default=False)


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, index=True)
    
    role = Column(String)  # user, assistant, system
    content = Column(Text)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer, nullable=True)
    
    tool_calls = Column(Text, nullable=True)  # JSON string
    metadata = Column(Text, nullable=True)  # JSON string


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    source = Column(String)  # File path or URL
    category = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    indexed = Column(Boolean, default=False)
    vector_id = Column(String, nullable=True)  # Chroma document ID