"""
Evolution API endpoints for WhatsApp integration.
Handles Evolution API instance management and QR code operations.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import logging

from app.core.config import get_settings
from app.services.evolution_service import EvolutionAPIService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/evolution", tags=["Evolution API"])

# Pydantic models for request/response
class CreateInstanceRequest(BaseModel):
    """Request model for creating Evolution API instance."""
    name: str
    webhook_url: Optional[str] = None

class InstanceResponse(BaseModel):
    """Response model for instance operations."""
    success: bool
    message: str
    data: Optional[dict] = None

class QRCodeResponse(BaseModel):
    """Response model for QR code operations."""
    success: bool
    qr_code: Optional[str] = None
    message: str

class InstanceStateResponse(BaseModel):
    """Response model for instance state."""
    success: bool
    state: Optional[str] = None
    message: str


@router.post("/instances", response_model=InstanceResponse)
async def create_instance(request: CreateInstanceRequest):
    """
    Create a new Evolution API instance.
    
    Args:
        request: Instance creation parameters
    
    Returns:
        InstanceResponse with creation result
    """
    try:
        settings = get_settings()
        
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Evolution API not configured. Please set EVOLUTION_API_URL and EVOLUTION_API_KEY."
            )
        
        evolution_service = EvolutionAPIService()
        result = await evolution_service.create_instance(
            instance_name=request.name,
            webhook_url=request.webhook_url
        )
        
        logger.info(f"✅ Evolution instance created: {request.name}")
        
        return InstanceResponse(
            success=True,
            message="Instance created successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to create Evolution instance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_name}/qr", response_model=QRCodeResponse)
async def get_qr_code(instance_name: str):
    """
    Get QR code for WhatsApp connection.
    
    Args:
        instance_name: Name of the Evolution API instance
    
    Returns:
        QRCodeResponse with QR code data
    """
    try:
        settings = get_settings()
        
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Evolution API not configured"
            )
        
        evolution_service = EvolutionAPIService()
        result = await evolution_service.get_qr_code(instance_name)
        
        if result.get("success") and result.get("qr_code"):
            logger.info(f"✅ QR code retrieved for instance: {instance_name}")
            return QRCodeResponse(
                success=True,
                qr_code=result["qr_code"],
                message="QR code retrieved successfully"
            )
        else:
            return QRCodeResponse(
                success=False,
                message=result.get("error", "QR code not available. Instance may already be connected.")
            )
        
    except Exception as e:
        logger.error(f"❌ Failed to get QR code for {instance_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/instances/{instance_name}/state", response_model=InstanceStateResponse)
async def get_instance_state(instance_name: str):
    """
    Get the current state of an Evolution API instance.
    
    Args:
        instance_name: Name of the Evolution API instance
    
    Returns:
        InstanceStateResponse with current state
    """
    try:
        settings = get_settings()
        
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Evolution API not configured"
            )
        
        evolution_service = EvolutionAPIService()
        result = await evolution_service.get_instance_state(instance_name)
        
        if result.get("success"):
            state = result.get("state")
            logger.info(f"📊 Instance {instance_name} state: {state}")
            
            return InstanceStateResponse(
                success=True,
                state=state,
                message=f"Instance state: {state}"
            )
        else:
            logger.error(f"❌ Failed to get state for {instance_name}: {result.get('error')}")
            raise HTTPException(status_code=500, detail=result.get("error", "Failed to get instance state"))
        
    except Exception as e:
        logger.error(f"❌ Failed to get state for {instance_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/instances/{instance_name}", response_model=InstanceResponse)
async def delete_instance(instance_name: str):
    """
    Delete an Evolution API instance.
    
    Args:
        instance_name: Name of the Evolution API instance to delete
    
    Returns:
        InstanceResponse with deletion result
    """
    try:
        settings = get_settings()
        
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            raise HTTPException(
                status_code=500,
                detail="Evolution API not configured"
            )
        
        evolution_service = EvolutionAPIService()
        result = await evolution_service.delete_instance(instance_name)
        
        logger.info(f"🗑️  Evolution instance deleted: {instance_name}")
        
        return InstanceResponse(
            success=True,
            message="Instance deleted successfully",
            data=result
        )
        
    except Exception as e:
        logger.error(f"❌ Failed to delete Evolution instance {instance_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
