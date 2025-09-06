"""
Webhook Manager Service - Automatically manages Evolution API webhooks.
Handles webhook configuration, updates, and validation.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from app.core.config import get_settings
from app.services.evolution_service import evolution_service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Instance

logger = logging.getLogger(__name__)
settings = get_settings()


class WebhookManager:
    """
    Manages Evolution API webhooks automatically.
    Handles configuration updates, validation, and synchronization.
    """
    
    def __init__(self):
        self.current_webhook_url = None
        self.instances_configured = set()
    
    async def get_current_webhook_url(self) -> Optional[str]:
        """Get the current webhook URL from settings."""
        if settings.WEBHOOK_BASE_URL:
            return f"{settings.WEBHOOK_BASE_URL}/api/v1/webhooks/evolution"
        return None
    
    async def update_all_webhooks(self, db: AsyncSession) -> Dict[str, Any]:
        """
        Update webhooks for all active instances.
        
        Args:
            db: Database session
            
        Returns:
            Dict with update results
        """
        webhook_url = await self.get_current_webhook_url()
        if not webhook_url:
            logger.warning("No webhook base URL configured")
            return {"success": False, "error": "No webhook URL configured"}
        
        logger.info(f"🔄 Updating all webhooks to: {webhook_url}")
        
        # Get all active instances from database
        result = await db.execute(
            select(Instance).where(Instance.status.in_(["connected", "open", "connecting"]))
        )
        instances = result.scalars().all()
        
        results = {}
        success_count = 0
        
        for instance in instances:
            try:
                update_result = await self.update_instance_webhook(
                    instance.instance_name, 
                    webhook_url
                )
                results[instance.instance_name] = update_result
                
                if update_result.get("success"):
                    success_count += 1
                    self.instances_configured.add(instance.instance_name)
                    
            except Exception as e:
                logger.error(f"Error updating webhook for {instance.instance_name}: {e}")
                results[instance.instance_name] = {"success": False, "error": str(e)}
        
        logger.info(f"✅ Updated {success_count}/{len(instances)} webhooks successfully")
        
        return {
            "success": success_count > 0,
            "updated_count": success_count,
            "total_count": len(instances),
            "webhook_url": webhook_url,
            "results": results
        }
    
    async def update_instance_webhook(self, instance_name: str, webhook_url: str) -> Dict[str, Any]:
        """
        Update webhook for a specific instance.
        
        Args:
            instance_name: Name of the Evolution API instance
            webhook_url: New webhook URL
            
        Returns:
            Dict with update result
        """
        try:
            logger.info(f"🔧 Updating webhook for {instance_name}")
            
            # Use the evolution service to configure webhook
            result = await evolution_service.configure_webhook(instance_name, webhook_url)
            
            if result.get("success"):
                logger.info(f"✅ Webhook updated for {instance_name}")
                self.instances_configured.add(instance_name)
            else:
                logger.error(f"❌ Failed to update webhook for {instance_name}: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error updating webhook for {instance_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def validate_webhook_configuration(self, instance_name: str) -> Dict[str, Any]:
        """
        Validate that webhook is correctly configured for an instance.
        
        Args:
            instance_name: Name of the instance to validate
            
        Returns:
            Dict with validation result
        """
        try:
            # Try to get current webhook configuration
            # This would need to be implemented in evolution_service
            # For now, we'll assume it's configured if it's in our set
            is_configured = instance_name in self.instances_configured
            
            return {
                "success": True,
                "configured": is_configured,
                "instance": instance_name
            }
            
        except Exception as e:
            logger.error(f"Error validating webhook for {instance_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def ensure_webhook_configured(self, instance_name: str, db: AsyncSession) -> bool:
        """
        Ensure webhook is configured for a specific instance.
        If not configured, attempt to configure it.
        
        Args:
            instance_name: Name of the instance
            db: Database session
            
        Returns:
            True if webhook is configured, False otherwise
        """
        webhook_url = await self.get_current_webhook_url()
        if not webhook_url:
            logger.warning("No webhook URL configured")
            return False
        
        # Check if already configured
        if instance_name in self.instances_configured:
            return True
        
        # Try to configure it
        result = await self.update_instance_webhook(instance_name, webhook_url)
        return result.get("success", False)
    
    async def on_settings_change(self, db: AsyncSession):
        """
        Called when settings change (e.g., WEBHOOK_BASE_URL updated).
        Automatically updates all webhooks.
        
        Args:
            db: Database session
        """
        new_webhook_url = await self.get_current_webhook_url()
        
        if new_webhook_url != self.current_webhook_url:
            logger.info(f"🔄 Webhook URL changed: {self.current_webhook_url} → {new_webhook_url}")
            self.current_webhook_url = new_webhook_url
            
            if new_webhook_url:
                # Clear configured instances since URL changed
                self.instances_configured.clear()
                
                # Update all webhooks
                await self.update_all_webhooks(db)
            else:
                logger.warning("⚠️  Webhook URL is now None - webhooks disabled")


# Global webhook manager instance
webhook_manager = WebhookManager()

