"""
API endpoints for managing agent configurations.
This allows users to create, update, and manage their agent's behavior through the frontend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from typing import List, Optional
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.database.connection import get_async_db
from app.models.database import AgentConfig, Instance
from app.core.config import get_settings

router = APIRouter(prefix="/agent-configs", tags=["Agent Configurations"])

# Pydantic models for request/response
class AgentConfigCreate(BaseModel):
    instance_name: str
    agent_name: str
    agent_purpose: str
    agent_behavior: str
    working_hours_start: str = "09:00"
    working_hours_end: str = "18:00"
    timezone: str = "America/Bogota"
    language: str = "es"
    greeting_message: Optional[str] = None
    fallback_message: Optional[str] = None
    booking_instructions: Optional[str] = None
    custom_prompts: Optional[dict] = None

class AgentConfigUpdate(BaseModel):
    agent_name: Optional[str] = None
    agent_purpose: Optional[str] = None
    agent_behavior: Optional[str] = None
    working_hours_start: Optional[str] = None
    working_hours_end: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    greeting_message: Optional[str] = None
    fallback_message: Optional[str] = None
    booking_instructions: Optional[str] = None
    custom_prompts: Optional[dict] = None
    is_active: Optional[bool] = None

class AgentConfigResponse(BaseModel):
    id: str
    instance_name: str
    agent_name: str
    agent_purpose: str
    agent_behavior: str
    working_hours_start: str
    working_hours_end: str
    timezone: str
    language: str
    greeting_message: Optional[str]
    fallback_message: Optional[str]
    booking_instructions: Optional[str]
    custom_prompts: Optional[dict]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/", response_model=AgentConfigResponse)
async def create_agent_config(
    config_data: AgentConfigCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new agent configuration for a WhatsApp instance."""
    try:
        # Check if instance exists
        instance_result = await db.execute(
            select(Instance).where(Instance.instance_name == config_data.instance_name)
        )
        instance = instance_result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"WhatsApp instance '{config_data.instance_name}' not found"
            )
        
        # Check if agent config already exists for this instance
        existing_config_result = await db.execute(
            select(AgentConfig).where(AgentConfig.instance_name == config_data.instance_name)
        )
        if existing_config_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Agent configuration already exists for instance '{config_data.instance_name}'"
            )
        
        # Create new agent configuration
        agent_config = AgentConfig(
            id=str(uuid.uuid4()),
            instance_name=config_data.instance_name,
            agent_name=config_data.agent_name,
            agent_purpose=config_data.agent_purpose,
            agent_behavior=config_data.agent_behavior,
            working_hours_start=config_data.working_hours_start,
            working_hours_end=config_data.working_hours_end,
            timezone=config_data.timezone,
            language=config_data.language,
            greeting_message=config_data.greeting_message,
            fallback_message=config_data.fallback_message,
            booking_instructions=config_data.booking_instructions,
            custom_prompts=config_data.custom_prompts or {},
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        db.add(agent_config)
        await db.commit()
        await db.refresh(agent_config)
        
        return agent_config
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agent configuration: {str(e)}"
        )

@router.get("/", response_model=List[AgentConfigResponse])
async def get_agent_configs(
    instance_name: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get agent configurations with optional filtering."""
    try:
        # Use the same pattern as other working endpoints
        result = await db.execute(select(AgentConfig))
        configs = result.scalars().all()
        
        return configs
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agent configurations: {str(e)}"
        )

@router.get("/{config_id}", response_model=AgentConfigResponse)
async def get_agent_config(
    config_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific agent configuration by ID."""
    try:
        result = await db.execute(
            select(AgentConfig).where(AgentConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent configuration not found"
            )
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agent configuration: {str(e)}"
        )

@router.put("/{config_id}", response_model=AgentConfigResponse)
async def update_agent_config(
    config_id: str,
    config_data: AgentConfigUpdate,
    db: AsyncSession = Depends(get_async_db)
):
    """Update an existing agent configuration."""
    try:
        # Get existing configuration
        result = await db.execute(
            select(AgentConfig).where(AgentConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent configuration not found"
            )
        
        # Update fields
        update_data = config_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now()
            
            await db.execute(
                update(AgentConfig)
                .where(AgentConfig.id == config_id)
                .values(**update_data)
            )
            await db.commit()
            
            # Refresh the object
            await db.refresh(config)
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating agent configuration: {str(e)}"
        )

@router.delete("/{config_id}")
async def delete_agent_config(
    config_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete an agent configuration."""
    try:
        # Check if configuration exists
        result = await db.execute(
            select(AgentConfig).where(AgentConfig.id == config_id)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agent configuration not found"
            )
        
        # Delete configuration
        await db.execute(
            delete(AgentConfig).where(AgentConfig.id == config_id)
        )
        await db.commit()
        
        return {"message": "Agent configuration deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting agent configuration: {str(e)}"
        )

@router.get("/instance/{instance_name}", response_model=AgentConfigResponse)
async def get_agent_config_by_instance(
    instance_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Get agent configuration for a specific WhatsApp instance."""
    try:
        result = await db.execute(
            select(AgentConfig).where(AgentConfig.instance_name == instance_name)
        )
        config = result.scalar_one_or_none()
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No agent configuration found for instance '{instance_name}'"
            )
        
        return config
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving agent configuration: {str(e)}"
        )
