"""
Database models for the Agendo application.
Defines the structure of all database tables using SQLAlchemy.
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid


Base = declarative_base()


def generate_uuid():
    """Generate a unique UUID string."""
    return str(uuid.uuid4())


class Instance(Base):
    """
    WhatsApp instances created through Evolution API.
    Each instance represents a connected WhatsApp number.
    """
    __tablename__ = "instances"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    instance_name = Column(String, unique=True, nullable=False, index=True)
    evolution_instance_id = Column(String, nullable=True)  # Evolution API instance ID
    phone_number = Column(String, nullable=True)
    owner_jid = Column(String, nullable=True)  # WhatsApp JID
    profile_name = Column(String, nullable=True)
    profile_pic_url = Column(String, nullable=True)
    status = Column(String, default="connecting")  # connecting, connected, disconnected
    qr_code = Column(Text, nullable=True)
    webhook_url = Column(String, nullable=True)
    
    # Evolution API data
    token = Column(String, nullable=True)
    client_name = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    connected_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    agent_config = relationship("AgentConfig", back_populates="instance", uselist=False)
    conversations = relationship("Conversation", back_populates="instance")


class AgentConfig(Base):
    """
    Configuration for conversational agents.
    Stores the context, behavior, and settings for each WhatsApp instance.
    """
    __tablename__ = "agent_configs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    instance_id = Column(String, ForeignKey("instances.id"), nullable=False, unique=True)
    
    # Agent identity and behavior
    agent_name = Column(String, nullable=False)
    agent_purpose = Column(Text, nullable=False)  # Business description
    agent_behavior = Column(Text, nullable=False)  # How the agent should behave
    business_context = Column(Text, nullable=True)  # Additional context
    
    # Working hours configuration
    working_hours_enabled = Column(Boolean, default=True)
    working_hours_start = Column(String, default="09:00")  # HH:MM format
    working_hours_end = Column(String, default="18:00")    # HH:MM format
    timezone = Column(String, default="America/Bogota")
    
    # Google Calendar integration
    google_calendar_connected = Column(Boolean, default=False)
    google_access_token = Column(Text, nullable=True)
    google_refresh_token = Column(Text, nullable=True)
    google_token_expires_at = Column(DateTime(timezone=True), nullable=True)
    google_email = Column(String, nullable=True)
    
    # Agent status
    is_active = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    instance = relationship("Instance", back_populates="agent_config")


class Conversation(Base):
    """
    Conversation threads between customers and agents.
    Tracks ongoing conversations for context and history.
    """
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    instance_id = Column(String, ForeignKey("instances.id"), nullable=False)
    customer_phone = Column(String, nullable=False)
    customer_name = Column(String, nullable=True)
    
    # Conversation state
    status = Column(String, default="active")  # active, closed, archived
    last_message_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Context for the conversation (stored as JSON)
    context = Column(JSON, default=dict)  # Store conversation state, booking info, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    instance = relationship("Instance", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    """
    Individual messages within conversations.
    Stores both incoming and outgoing messages.
    """
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    content = Column(Text, nullable=False)
    message_type = Column(String, default="text")  # text, image, document, etc.
    direction = Column(String, nullable=False)  # incoming, outgoing
    
    # WhatsApp message metadata
    whatsapp_message_id = Column(String, nullable=True)
    sender_phone = Column(String, nullable=True)  # For incoming messages
    
    # Processing status
    processed = Column(Boolean, default=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class CalendarEvent(Base):
    """
    Calendar events created by the agent.
    Tracks appointments booked through conversations.
    """
    __tablename__ = "calendar_events"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    instance_id = Column(String, ForeignKey("instances.id"), nullable=False)
    conversation_id = Column(String, ForeignKey("conversations.id"), nullable=True)
    
    # Event details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    # Customer information
    customer_name = Column(String, nullable=True)
    customer_phone = Column(String, nullable=True)
    customer_email = Column(String, nullable=True)
    
    # Google Calendar integration
    google_event_id = Column(String, nullable=True)
    google_event_url = Column(String, nullable=True)
    
    # Event status
    status = Column(String, default="scheduled")  # scheduled, confirmed, cancelled, completed
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conversation = relationship("Conversation")
    instance = relationship("Instance")

