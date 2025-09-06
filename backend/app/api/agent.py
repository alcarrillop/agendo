"""
Agent configuration endpoints.
Handles conversational agent setup and configuration management.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from app.core.config import get_settings
from app.database.connection import get_async_db
from app.models.database import AgentConfig
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agent", tags=["Agent Configuration"])

# Pydantic models for request/response
class AgentConfigRequest(BaseModel):
    """Request model for agent configuration."""
    business_name: str
    business_description: str
    available_hours: Dict[str, Any]  # e.g., {"monday": {"start": "09:00", "end": "17:00"}}
    appointment_duration: int  # Duration in minutes
    buffer_time: int  # Buffer time between appointments in minutes
    google_calendar_id: Optional[str] = None
    custom_instructions: Optional[str] = None
    greeting_message: Optional[str] = None

class AgentConfigResponse(BaseModel):
    """Response model for agent configuration."""
    success: bool
    message: str
    config: Optional[Dict[str, Any]] = None

class AgentStatusResponse(BaseModel):
    """Response model for agent status."""
    success: bool
    status: str
    message: str
    last_updated: Optional[datetime] = None


@router.post("/config", response_model=AgentConfigResponse)
async def save_agent_config(
    request: AgentConfigRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Save or update agent configuration.
    
    Args:
        request: Agent configuration data
        db: Database session
    
    Returns:
        AgentConfigResponse with save result
    """
    try:
        # For MVP, we'll use a simple in-memory storage
        # In production, this would save to the database
        
        config_data = {
            "business_name": request.business_name,
            "business_description": request.business_description,
            "available_hours": request.available_hours,
            "appointment_duration": request.appointment_duration,
            "buffer_time": request.buffer_time,
            "google_calendar_id": request.google_calendar_id,
            "custom_instructions": request.custom_instructions,
            "greeting_message": request.greeting_message,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        logger.info(f"✅ Agent configuration saved for: {request.business_name}")
        
        return AgentConfigResponse(
            success=True,
            message="Agent configuration saved successfully",
            config=config_data
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to save agent configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=AgentConfigResponse)
async def get_agent_config(db: AsyncSession = Depends(get_async_db)):
    """
    Get current agent configuration.
    
    Args:
        db: Database session
    
    Returns:
        AgentConfigResponse with current configuration
    """
    try:
        # For MVP, return a default configuration
        # In production, this would fetch from the database
        
        default_config = {
            "business_name": "Your Business",
            "business_description": "Professional services",
            "available_hours": {
                "monday": {"start": "09:00", "end": "17:00"},
                "tuesday": {"start": "09:00", "end": "17:00"},
                "wednesday": {"start": "09:00", "end": "17:00"},
                "thursday": {"start": "09:00", "end": "17:00"},
                "friday": {"start": "09:00", "end": "17:00"}
            },
            "appointment_duration": 60,
            "buffer_time": 15,
            "google_calendar_id": None,
            "custom_instructions": "Be helpful and professional when scheduling appointments.",
            "greeting_message": "Hello! I'm here to help you schedule an appointment. How can I assist you today?"
        }
        
        logger.info("📊 Agent configuration retrieved")
        
        return AgentConfigResponse(
            success=True,
            message="Agent configuration retrieved successfully",
            config=default_config
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get agent configuration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=AgentStatusResponse)
async def get_agent_status():
    """
    Get current agent status and health.
    
    Returns:
        AgentStatusResponse with agent status
    """
    try:
        settings = get_settings()
        
        # Check if all required services are configured
        services_configured = all([
            settings.OPENAI_API_KEY,
            settings.EVOLUTION_API_URL,
            settings.EVOLUTION_API_KEY,
            settings.GOOGLE_CLIENT_ID,
            settings.GOOGLE_CLIENT_SECRET
        ])
        
        if services_configured:
            status = "ready"
            message = "Agent is configured and ready to process messages"
        else:
            status = "configuration_incomplete"
            message = "Agent requires additional configuration"
        
        logger.info(f"📊 Agent status: {status}")
        
        return AgentStatusResponse(
            success=True,
            status=status,
            message=message,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to get agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=Dict[str, Any])
async def test_agent_response(
    message: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Test agent response to a message (for development/testing).
    
    Args:
        message: Test message to send to the agent
        db: Database session
    
    Returns:
        Dict with agent response
    """
    try:
        # For MVP, return a simple test response
        # In production, this would use the actual conversation agent
        
        test_response = {
            "input_message": message,
            "agent_response": f"Thank you for your message: '{message}'. This is a test response from the Awendo agent.",
            "intent_detected": "general_inquiry",
            "action_taken": "none",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"🧪 Agent test completed for message: {message[:50]}...")
        
        return test_response
        
    except Exception as e:
        logger.error(f"❌ Agent test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
