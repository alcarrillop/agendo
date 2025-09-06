"""
Webhook Management API endpoints.
Provides endpoints for managing Evolution API webhooks.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import get_async_db
from app.services.webhook_manager import webhook_manager
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks", tags=["webhook-management"])


class WebhookUpdateRequest(BaseModel):
    """Request model for webhook updates."""
    instance_name: Optional[str] = None  # If None, update all instances
    webhook_url: Optional[str] = None    # If None, use current settings


class WebhookUpdateResponse(BaseModel):
    """Response model for webhook updates."""
    success: bool
    message: str
    updated_count: Optional[int] = None
    total_count: Optional[int] = None
    webhook_url: Optional[str] = None
    results: Optional[Dict[str, Any]] = None


@router.post("/update", response_model=WebhookUpdateResponse)
async def update_webhooks(
    request: WebhookUpdateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Update webhooks for Evolution API instances.
    
    - If instance_name is provided, updates only that instance
    - If instance_name is None, updates all instances
    - If webhook_url is provided, uses that URL
    - If webhook_url is None, uses current WEBHOOK_BASE_URL from settings
    """
    try:
        logger.info(f"📡 Webhook update request: {request}")
        
        if request.instance_name:
            # Update specific instance
            webhook_url = request.webhook_url or await webhook_manager.get_current_webhook_url()
            if not webhook_url:
                raise HTTPException(
                    status_code=400, 
                    detail="No webhook URL provided and WEBHOOK_BASE_URL not configured"
                )
            
            result = await webhook_manager.update_instance_webhook(
                request.instance_name, 
                webhook_url
            )
            
            if result.get("success"):
                return WebhookUpdateResponse(
                    success=True,
                    message=f"Webhook updated for {request.instance_name}",
                    updated_count=1,
                    total_count=1,
                    webhook_url=webhook_url
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to update webhook: {result.get('error')}"
                )
        else:
            # Update all instances
            result = await webhook_manager.update_all_webhooks(db)
            
            return WebhookUpdateResponse(
                success=result.get("success", False),
                message=f"Updated {result.get('updated_count', 0)}/{result.get('total_count', 0)} webhooks",
                updated_count=result.get("updated_count"),
                total_count=result.get("total_count"),
                webhook_url=result.get("webhook_url"),
                results=result.get("results")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def webhook_status(db: AsyncSession = Depends(get_async_db)):
    """Get current webhook configuration status."""
    try:
        current_url = await webhook_manager.get_current_webhook_url()
        
        return {
            "success": True,
            "current_webhook_url": current_url,
            "configured_instances": list(webhook_manager.instances_configured),
            "webhook_base_url_configured": bool(current_url)
        }
        
    except Exception as e:
        logger.error(f"Error getting webhook status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate/{instance_name}")
async def validate_instance_webhook(
    instance_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Validate webhook configuration for a specific instance."""
    try:
        result = await webhook_manager.validate_webhook_configuration(instance_name)
        
        return {
            "success": True,
            "instance_name": instance_name,
            "configured": result.get("configured", False),
            "validation_result": result
        }
        
    except Exception as e:
        logger.error(f"Error validating webhook for {instance_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ensure/{instance_name}")
async def ensure_instance_webhook(
    instance_name: str,
    db: AsyncSession = Depends(get_async_db)
):
    """Ensure webhook is configured for a specific instance."""
    try:
        configured = await webhook_manager.ensure_webhook_configured(instance_name, db)
        
        return {
            "success": True,
            "instance_name": instance_name,
            "configured": configured,
            "message": "Webhook configured" if configured else "Failed to configure webhook"
        }
        
    except Exception as e:
        logger.error(f"Error ensuring webhook for {instance_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh")
async def refresh_webhooks(db: AsyncSession = Depends(get_async_db)):
    """
    Refresh all webhooks based on current settings.
    This is useful when WEBHOOK_BASE_URL has changed.
    """
    try:
        logger.info("🔄 Refreshing all webhooks...")
        
        # Trigger settings change handler
        await webhook_manager.on_settings_change(db)
        
        return {
            "success": True,
            "message": "Webhooks refreshed successfully",
            "current_webhook_url": await webhook_manager.get_current_webhook_url()
        }
        
    except Exception as e:
        logger.error(f"Error refreshing webhooks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

