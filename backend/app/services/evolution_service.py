"""
Service for interacting with Evolution API (WhatsApp integration).
Handles sending messages, managing instances, and processing webhooks.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class EvolutionAPIService:
    """
    Service class for Evolution API integration.
    Provides methods to interact with WhatsApp through Evolution API.
    """
    
    def __init__(self):
        """Initialize the Evolution API service."""
        self.base_url = settings.EVOLUTION_API_URL
        self.api_key = settings.EVOLUTION_API_KEY
        
        if not self.base_url:
            logger.warning("Evolution API URL not configured")
            
        # Default headers for API requests
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Add API key to headers if configured
        if self.api_key:
            self.headers["apikey"] = self.api_key
    
    async def send_message(
        self, 
        instance_name: str, 
        to: str, 
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message through Evolution API.
        
        Args:
            instance_name: Name of the WhatsApp instance
            to: Recipient phone number
            message: Message content to send
            message_type: Type of message (text, image, document, etc.)
            
        Returns:
            Dict containing the API response
        """
        if not self.base_url:
            raise ValueError("Evolution API URL not configured")
            
        url = f"{self.base_url}/message/sendText/{instance_name}"
        
        # Ensure phone number is in correct format for Evolution API
        phone_number = to
        if '@' not in phone_number:
            phone_number = f"{phone_number}@s.whatsapp.net"
        
        payload = {
            "number": phone_number,
            "text": message
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Message sent successfully to {to} via instance {instance_name}")
                return {
                    "success": True,
                    "message_id": result.get("key", {}).get("id"),
                    "response": result
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending message: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_instance_state(self, instance_name: str) -> Dict[str, Any]:
        """
        Get the connection state of a WhatsApp instance.
        
        Args:
            instance_name: Name of the WhatsApp instance
            
        Returns:
            Dict containing the instance state information
        """
        if not self.base_url:
            raise ValueError("Evolution API URL not configured")
            
        url = f"{self.base_url}/instance/connectionState/{instance_name}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": True,
                    "state": result.get("instance", {}).get("state"),
                    "response": result
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting instance state: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error getting instance state: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_instance(
        self, 
        instance_name: str, 
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new WhatsApp instance in Evolution API.
        
        Args:
            instance_name: Name for the new instance
            webhook_url: URL to receive webhooks (optional)
            
        Returns:
            Dict containing the creation result and QR code
        """
        if not self.base_url:
            raise ValueError("Evolution API URL not configured")
            
        url = f"{self.base_url}/instance/create"
        
        payload = {
            "instanceName": instance_name,
            "integration": "WHATSAPP-BAILEYS",
            "qrcode": True
        }
        
        # Note: Webhook will be configured separately after instance creation
        # Evolution API has issues with webhook URLs during creation
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=60.0  # Instance creation can take longer
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Instance {instance_name} created successfully")
                return {
                    "success": True,
                    "instance_name": instance_name,
                    "response": result
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error creating instance: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error creating instance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_qr_code(self, instance_name: str) -> Dict[str, Any]:
        """
        Get the QR code for a WhatsApp instance.
        
        Args:
            instance_name: Name of the WhatsApp instance
            
        Returns:
            Dict containing the QR code data
        """
        if not self.base_url:
            raise ValueError("Evolution API URL not configured")
            
        url = f"{self.base_url}/instance/connect/{instance_name}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                return {
                    "success": True,
                    "qr_code": result.get("qr"),
                    "response": result
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting QR code: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error getting QR code: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_instance(self, instance_name: str) -> Dict[str, Any]:
        """
        Delete a WhatsApp instance from Evolution API.
        
        Args:
            instance_name: Name of the instance to delete
            
        Returns:
            Dict containing the deletion result
        """
        if not self.base_url:
            raise ValueError("Evolution API URL not configured")
            
        url = f"{self.base_url}/instance/delete/{instance_name}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                response.raise_for_status()
                result = response.json()
                
                logger.info(f"Instance {instance_name} deleted successfully")
                return {
                    "success": True,
                    "response": result
                }
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error deleting instance: {e}")
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error deleting instance: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def parse_webhook_message(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse incoming webhook message from Evolution API.
        
        Args:
            webhook_data: Raw webhook data from Evolution API
            
        Returns:
            Parsed message data or None if not a valid message
        """
        try:
            event = webhook_data.get("event")
            instance = webhook_data.get("instance")
            data = webhook_data.get("data", {})
            
            # Log the entire webhook for debugging
            logger.info(f"🔍 DEBUG - Full webhook data: {webhook_data}")
            
            if event == "messages.upsert":
                # Handle both array format and single message format
                messages = data.get("messages", [])
                
                # If no messages array, check if data itself is the message
                if not messages and "key" in data and "message" in data:
                    messages = [data]
                    logger.info(f"🔍 DEBUG - Found single message in data (not array format)")
                else:
                    logger.info(f"🔍 DEBUG - Found {len(messages)} messages in webhook")
                
                for i, message in enumerate(messages):
                    logger.info(f"🔍 DEBUG - Message {i}: {message}")
                    
                    # Only process incoming messages (not sent by us)
                    key = message.get("key", {})
                    from_me = key.get("fromMe", False)
                    
                    logger.info(f"🔍 DEBUG - fromMe: {from_me}")
                    
                    if not from_me:
                        message_obj = message.get("message", {})
                        logger.info(f"🔍 DEBUG - Message object: {message_obj}")
                        
                        # Extract message content from different possible sources
                        content = None
                        message_type = "unknown"
                        
                        # Try different message types with more options
                        if "conversation" in message_obj:
                            content = message_obj.get("conversation")
                            message_type = "conversation"
                        elif "extendedTextMessage" in message_obj:
                            content = message_obj.get("extendedTextMessage", {}).get("text")
                            message_type = "extendedTextMessage"
                        elif "textMessage" in message_obj:
                            content = message_obj.get("textMessage", {}).get("text")
                            message_type = "textMessage"
                        elif "imageMessage" in message_obj:
                            content = message_obj.get("imageMessage", {}).get("caption", "[Imagen]")
                            message_type = "imageMessage"
                        elif "documentMessage" in message_obj:
                            content = message_obj.get("documentMessage", {}).get("caption", "[Documento]")
                            message_type = "documentMessage"
                        else:
                            # Try to find any text content in the message
                            for key_name, value in message_obj.items():
                                if isinstance(value, dict) and "text" in value:
                                    content = value["text"]
                                    message_type = key_name
                                    break
                                elif isinstance(value, str) and len(value.strip()) > 0:
                                    content = value
                                    message_type = key_name
                                    break
                        
                        logger.info(f"🔍 DEBUG - Extracted content: '{content}', type: {message_type}")
                        
                        if content and content.strip():
                            result = {
                                "instance_name": instance,
                                "from": key.get("remoteJid"),
                                "message_id": key.get("id"),
                                "content": content.strip(),
                                "message_type": message_type,
                                "timestamp": message.get("messageTimestamp")
                            }
                            logger.info(f"✅ Successfully parsed message: {result}")
                            return result
                        else:
                            logger.warning(f"⚠️ No valid content found in message: {message_obj}")
            
            logger.info("ℹ️ No valid incoming message found in webhook")
            return None
            
        except Exception as e:
            logger.error(f"❌ Error parsing webhook message: {e}")
            logger.error(f"❌ Webhook data was: {webhook_data}")
            return None
    
    async def configure_webhook(
        self, 
        instance_name: str, 
        webhook_url: str
    ) -> Dict[str, Any]:
        """
        Configure webhook for an existing instance.
        
        Args:
            instance_name: Name of the instance
            webhook_url: URL to receive webhooks
            
        Returns:
            Dict containing the configuration result
        """
        if not self.base_url:
            return {
                "success": False,
                "error": "Evolution API URL not configured"
            }
        
        # Try different webhook configuration endpoints
        endpoints_to_try = [
            f"{self.base_url}/webhook/set/{instance_name}",
            f"{self.base_url}/instance/update/{instance_name}",
            f"{self.base_url}/webhook/{instance_name}"
        ]
        
        for url in endpoints_to_try:
            try:
                async with httpx.AsyncClient() as client:
                    # Prepare payload based on endpoint
                    if "webhook/set" in url:
                        payload = {
                            "url": webhook_url,
                            "events": ["MESSAGES_UPSERT", "CONNECTION_UPDATE"],
                            "webhook_by_events": True
                        }
                    else:
                        payload = {
                            "webhook": webhook_url,
                            "webhook_by_events": True
                        }
                    
                    response = await client.post(
                        url,
                        json=payload,
                        headers=self.headers,
                        timeout=30.0
                    )
                    
                    if response.status_code in [200, 201]:
                        logger.info(f"✅ Webhook configured for {instance_name} using {url}")
                        return {
                            "success": True,
                            "webhook_url": webhook_url,
                            "endpoint_used": url
                        }
                    else:
                        logger.warning(f"Failed to configure webhook via {url}: {response.status_code}")
                        continue
                        
            except Exception as e:
                logger.warning(f"Error configuring webhook via {url}: {e}")
                continue
        
        logger.error(f"Failed to configure webhook for {instance_name} - all endpoints failed")
        return {
            "success": False,
            "error": "All webhook configuration endpoints failed"
        }


# Global service instance
evolution_service = EvolutionAPIService()

