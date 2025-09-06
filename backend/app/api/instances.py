"""
API endpoints for managing WhatsApp instances.
Handles creation, retrieval, and management of WhatsApp instances.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from app.database.connection import get_async_db
from app.services.instance_service import instance_service
from app.models.database import Instance

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/instances", tags=["instances"])


class CreateInstanceRequest(BaseModel):
    """Request model for creating a new instance."""
    instance_name: str
    user_id: Optional[str] = None


class InstanceResponse(BaseModel):
    """Response model for instance data."""
    id: str
    instance_name: str
    evolution_instance_id: Optional[str]
    status: str
    phone_number: Optional[str]
    owner_jid: Optional[str]
    profile_name: Optional[str]
    profile_pic_url: Optional[str]
    webhook_url: Optional[str]
    created_at: str
    connected_at: Optional[str]


class CreateInstanceResponse(BaseModel):
    """Response model for instance creation."""
    success: bool
    instance: Optional[dict] = None
    qrcode: Optional[dict] = None
    error: Optional[str] = None


@router.post("/sync", response_model=dict)
async def sync_instance(
    instance_data: dict,
    db: AsyncSession = Depends(get_async_db)
):
    """Sync an existing Evolution API instance to the database."""
    try:
        # Crear instancia en la base de datos
        instance = Instance(
            instance_name=instance_data.get("instance_name"),
            evolution_instance_id=instance_data.get("evolution_instance_id"),
            status=instance_data.get("status", "connecting"),
            phone_number=instance_data.get("phone_number"),
            owner_jid=instance_data.get("owner_jid"),
            profile_name=instance_data.get("profile_name"),
            profile_pic_url=instance_data.get("profile_pic_url"),
            webhook_url=instance_data.get("webhook_url"),
            token=instance_data.get("token"),
            client_name=instance_data.get("client_name", "evolution_exchange")
        )
        
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        
        logger.info(f"✅ Instance synced: {instance.instance_name}")
        
        return {
            "success": True,
            "message": f"Instance {instance.instance_name} synced successfully",
            "instance_id": str(instance.id)
        }
        
    except Exception as e:
        logger.error(f"❌ Error syncing instance: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to sync instance: {str(e)}")


@router.delete("/{instance_id}")
async def delete_instance(
    instance_id: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Delete an instance from the database."""
    try:
        # Find and delete the instance
        result = await db.execute(
            select(Instance).where(Instance.id == instance_id)
        )
        instance = result.scalar_one_or_none()
        
        if not instance:
            raise HTTPException(status_code=404, detail="Instance not found")
        
        await db.delete(instance)
        await db.commit()
        
        logger.info(f"✅ Instance deleted: {instance.instance_name}")
        
        return {
            "success": True,
            "message": f"Instance {instance.instance_name} deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"❌ Error deleting instance: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete instance: {str(e)}")


@router.post("/create", response_model=CreateInstanceResponse)
async def create_instance(
    request: CreateInstanceRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a new WhatsApp instance.
    
    Args:
        request: Instance creation request
        background_tasks: Background tasks for async operations
        db: Database session
        
    Returns:
        Instance creation response with QR code
    """
    try:
        logger.info(f"Creating instance: {request.instance_name}")
        
        # Check if instance already exists
        existing_instance = await instance_service.get_instance_by_name(
            db, request.instance_name
        )
        
        if existing_instance:
            raise HTTPException(
                status_code=400,
                detail=f"Instance '{request.instance_name}' already exists"
            )
        
        # Create instance
        result = await instance_service.create_instance(
            db=db,
            instance_name=request.instance_name,
            user_id=request.user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create instance: {result.get('error')}"
            )
        
        logger.info(f"✅ Instance created successfully: {request.instance_name}")
        
        return CreateInstanceResponse(
            success=True,
            instance=result["instance"],
            qrcode=result["qrcode"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating instance {request.instance_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/", response_model=List[InstanceResponse])
async def get_instances(
    active_only: bool = False,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all instances or only active ones.
    
    Args:
        active_only: If True, return only connected instances
        db: Database session
        
    Returns:
        List of instances
    """
    try:
        if active_only:
            instances = await instance_service.get_active_instances(db)
        else:
            # Get all instances
            from sqlalchemy import select
            result = await db.execute(select(Instance).order_by(Instance.created_at.desc()))
            instances = result.scalars().all()
        
        return [
            InstanceResponse(
                id=instance.id,
                instance_name=instance.instance_name,
                evolution_instance_id=instance.evolution_instance_id,
                status=instance.status,
                phone_number=instance.phone_number,
                owner_jid=instance.owner_jid,
                profile_name=instance.profile_name,
                profile_pic_url=instance.profile_pic_url,
                webhook_url=instance.webhook_url,
                created_at=instance.created_at.isoformat(),
                connected_at=instance.connected_at.isoformat() if instance.connected_at else None
            )
            for instance in instances
        ]
        
    except Exception as e:
        logger.error(f"Error getting instances: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{instance_name}", response_model=InstanceResponse)
async def get_instance(
    instance_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get instance by name.
    
    Args:
        instance_name: Name of the instance
        db: Database session
        
    Returns:
        Instance data
    """
    try:
        instance = await instance_service.get_instance_by_name(db, instance_name)
        
        if not instance:
            raise HTTPException(
                status_code=404,
                detail=f"Instance '{instance_name}' not found"
            )
        
        return InstanceResponse(
            id=instance.id,
            instance_name=instance.instance_name,
            evolution_instance_id=instance.evolution_instance_id,
            status=instance.status,
            phone_number=instance.phone_number,
            owner_jid=instance.owner_jid,
            profile_name=instance.profile_name,
            profile_pic_url=instance.profile_pic_url,
            webhook_url=instance.webhook_url,
            created_at=instance.created_at.isoformat(),
            connected_at=instance.connected_at.isoformat() if instance.connected_at else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting instance {instance_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{instance_name}")
async def delete_instance(
    instance_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Delete instance from both Evolution API and database.
    
    Args:
        instance_name: Name of the instance to delete
        db: Database session
        
    Returns:
        Deletion result
    """
    try:
        result = await instance_service.delete_instance(db, instance_name)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete instance: {result.get('error')}"
            )
        
        return {
            "success": True,
            "message": f"Instance '{instance_name}' deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting instance {instance_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

