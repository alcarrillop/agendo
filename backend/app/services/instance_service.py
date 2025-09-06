"""
Instance Service for managing WhatsApp instances with Evolution API.
Handles creation, persistence, and lifecycle management of WhatsApp instances.
"""

import logging
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from app.models.database import Instance
from app.services.evolution_service import evolution_service
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class InstanceService:
    """
    Service for managing WhatsApp instances.
    Handles both Evolution API integration and database persistence.
    """
    
    def __init__(self):
        self.webhook_base_url = settings.WEBHOOK_BASE_URL or "http://localhost:8000"
    
    async def create_instance(
        self, 
        db: AsyncSession, 
        instance_name: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new WhatsApp instance with Evolution API and persist in database.
        
        Args:
            db: Database session
            instance_name: Unique name for the instance
            user_id: Optional user ID to associate with instance
            
        Returns:
            Dict containing instance data and QR code
        """
        try:
            logger.info(f"Creating instance: {instance_name}")
            
            # Generate webhook URL for this instance
            webhook_url = f"{self.webhook_base_url}/api/v1/webhooks/evolution"
            
            # Create instance in Evolution API (without webhook first)
            evolution_result = await evolution_service.create_instance(
                instance_name=instance_name
            )
            
            if not evolution_result.get("success"):
                raise Exception(f"Evolution API error: {evolution_result.get('error')}")
            
            # Extract data from Evolution API response
            instance_data = evolution_result.get("instance", {})
            qr_data = evolution_result.get("qrcode", {})
            
            # Create instance record in database
            db_instance = Instance(
                instance_name=instance_name,
                evolution_instance_id=instance_data.get("instanceId"),
                status="connecting",
                qr_code=qr_data.get("base64"),
                webhook_url=webhook_url,
                token=evolution_result.get("hash"),
                client_name=instance_data.get("integration", "WHATSAPP-BAILEYS")
            )
            
            db.add(db_instance)
            await db.commit()
            await db.refresh(db_instance)
            
            # Configure webhook after instance creation (background task)
            try:
                webhook_result = await evolution_service.configure_webhook(
                    instance_name=instance_name,
                    webhook_url=webhook_url
                )
                if webhook_result.get("success"):
                    logger.info(f"✅ Webhook configured for {instance_name}")
                else:
                    logger.warning(f"⚠️ Webhook configuration failed for {instance_name}: {webhook_result.get('error')}")
            except Exception as e:
                logger.warning(f"⚠️ Error configuring webhook for {instance_name}: {e}")
            
            logger.info(f"✅ Instance created successfully: {instance_name}")
            
            return {
                "success": True,
                "instance": {
                    "id": db_instance.id,
                    "instance_name": db_instance.instance_name,
                    "evolution_instance_id": db_instance.evolution_instance_id,
                    "status": db_instance.status,
                    "webhook_url": db_instance.webhook_url,
                    "created_at": db_instance.created_at.isoformat()
                },
                "qrcode": {
                    "base64": db_instance.qr_code,
                    "code": qr_data.get("code")
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating instance {instance_name}: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_instance_by_name(
        self, 
        db: AsyncSession, 
        instance_name: str
    ) -> Optional[Instance]:
        """
        Get instance by name from database.
        
        Args:
            db: Database session
            instance_name: Name of the instance
            
        Returns:
            Instance object or None
        """
        try:
            result = await db.execute(
                select(Instance)
                .options(selectinload(Instance.agent_config))
                .where(Instance.instance_name == instance_name)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting instance {instance_name}: {e}")
            return None
    
    async def update_instance_status(
        self,
        db: AsyncSession,
        instance_name: str,
        status: str,
        connection_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update instance status and connection data.
        
        Args:
            db: Database session
            instance_name: Name of the instance
            status: New status (connecting, connected, disconnected)
            connection_data: Optional connection data from webhook
            
        Returns:
            True if updated successfully
        """
        try:
            # Prepare update data
            update_data = {"status": status}
            
            if connection_data:
                if connection_data.get("ownerJid"):
                    update_data["owner_jid"] = connection_data["ownerJid"]
                if connection_data.get("profileName"):
                    update_data["profile_name"] = connection_data["profileName"]
                if connection_data.get("profilePicUrl"):
                    update_data["profile_pic_url"] = connection_data["profilePicUrl"]
                if status == "connected":
                    from datetime import datetime
                    update_data["connected_at"] = datetime.utcnow()
            
            # Update instance
            await db.execute(
                update(Instance)
                .where(Instance.instance_name == instance_name)
                .values(**update_data)
            )
            await db.commit()
            
            logger.info(f"✅ Instance {instance_name} status updated to: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating instance {instance_name}: {e}")
            await db.rollback()
            return False
    
    async def get_active_instances(self, db: AsyncSession) -> List[Instance]:
        """
        Get all active (connected) instances from database.
        
        Args:
            db: Database session
            
        Returns:
            List of active Instance objects
        """
        try:
            result = await db.execute(
                select(Instance)
                .options(selectinload(Instance.agent_config))
                .where(Instance.status == "connected")
                .order_by(Instance.created_at.desc())
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting active instances: {e}")
            return []
    
    async def delete_instance(
        self, 
        db: AsyncSession, 
        instance_name: str
    ) -> Dict[str, Any]:
        """
        Delete instance from both Evolution API and database.
        
        Args:
            db: Database session
            instance_name: Name of the instance to delete
            
        Returns:
            Dict with success status
        """
        try:
            # Get instance from database
            instance = await self.get_instance_by_name(db, instance_name)
            if not instance:
                return {"success": False, "error": "Instance not found"}
            
            # Delete from Evolution API
            evolution_result = await evolution_service.delete_instance(instance_name)
            
            # Delete from database regardless of Evolution API result
            await db.delete(instance)
            await db.commit()
            
            logger.info(f"✅ Instance deleted: {instance_name}")
            
            return {
                "success": True,
                "message": "Instance deleted successfully",
                "evolution_result": evolution_result
            }
            
        except Exception as e:
            logger.error(f"Error deleting instance {instance_name}: {e}")
            await db.rollback()
            return {
                "success": False,
                "error": str(e)
            }


# Global service instance
instance_service = InstanceService()
