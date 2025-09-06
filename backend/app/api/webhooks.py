"""
Webhook endpoints for receiving external events.
Handles Evolution API webhooks and other external integrations.
"""

from fastapi import APIRouter, Request, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
import logging
import uuid
from datetime import datetime

from app.database.connection import get_async_db
from app.models.database import Instance, Conversation, Message, AgentConfig
from app.services.evolution_service import evolution_service
from app.services.instance_service import instance_service
from app.agents.conversation_agent import ConversationAgent
from app.services.calendar_service import calendar_service

router = APIRouter(prefix="/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)


@router.post("/evolution")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Webhook endpoint for Evolution API events.
    Processes WhatsApp messages and connection updates.
    
    This endpoint:
    1. Receives webhook data from Evolution API
    2. Parses incoming messages
    3. Processes messages with the conversational agent
    4. Sends responses back through WhatsApp
    5. Handles appointment booking if needed
    """
    request_id = str(uuid.uuid4())[:8]
    logger.info(f"[{request_id}] Evolution webhook received")
    
    try:
        # Parse webhook data
        webhook_data = await request.json()
        logger.info(f"[{request_id}] Webhook event: {webhook_data.get('event')}")
        
        # Process the webhook in the background to return 200 immediately
        background_tasks.add_task(
            process_evolution_webhook,
            webhook_data,
            request_id,
            db
        )
        
        return {"success": True, "request_id": request_id}
        
    except Exception as e:
        logger.error(f"[{request_id}] Error processing webhook: {e}")
        return {"success": False, "error": str(e), "request_id": request_id}


async def process_evolution_webhook(
    webhook_data: Dict[str, Any],
    request_id: str,
    db: AsyncSession
):
    """
    Process Evolution API webhook data in the background.
    
    Args:
        webhook_data: Raw webhook data from Evolution API
        request_id: Unique request identifier for logging
        db: Database session
    """
    try:
        event = webhook_data.get("event")
        instance_name = webhook_data.get("instance")
        
        logger.info(f"[{request_id}] Processing event: {event} for instance: {instance_name}")
        
        if event == "connection.update":
            await handle_connection_update(webhook_data, request_id, db)
            
        elif event == "messages.upsert":
            await handle_incoming_message(webhook_data, request_id, db)
            
        elif event == "qrcode.updated":
            await handle_qr_code_update(webhook_data, request_id, db)
            
        else:
            logger.info(f"[{request_id}] Unhandled event type: {event}")
            
    except Exception as e:
        logger.error(f"[{request_id}] Error in background webhook processing: {e}")


async def handle_connection_update(
    webhook_data: Dict[str, Any],
    request_id: str,
    db: AsyncSession
):
    """
    Handle WhatsApp connection status updates.
    
    Args:
        webhook_data: Webhook data containing connection info
        request_id: Request identifier for logging
        db: Database session
    """
    try:
        instance_name = webhook_data.get("instance")
        data = webhook_data.get("data", {})
        state = data.get("state")
        
        logger.info(f"[{request_id}] Connection update for {instance_name}: {state}")
        
        # Update instance status in database
        # Note: This is a simplified implementation
        # In production, you'd want proper error handling and transactions
        
        if state == "open":
            logger.info(f"[{request_id}] 🎉 Instance {instance_name} connected successfully!")
            
        elif state == "close":
            logger.info(f"[{request_id}] ❌ Instance {instance_name} disconnected")
            
    except Exception as e:
        logger.error(f"[{request_id}] Error handling connection update: {e}")


async def handle_incoming_message(
    webhook_data: Dict[str, Any],
    request_id: str,
    db: AsyncSession
):
    """
    Handle incoming WhatsApp messages and process them with the conversational agent.
    
    Args:
        webhook_data: Webhook data containing message info
        request_id: Request identifier for logging
        db: Database session
    """
    try:
        # Parse the message from webhook data
        message_data = evolution_service.parse_webhook_message(webhook_data)
        
        if not message_data:
            logger.info(f"[{request_id}] No valid message found in webhook data")
            return
            
        instance_name = message_data["instance_name"]
        from_phone = message_data["from"].split('@')[0]  # Extract phone number
        message_content = message_data["content"]
        
        logger.info(f"[{request_id}] 📱 Message from {from_phone}: '{message_content}'")
        
        # Process the message with the conversational agent
        agent = ConversationAgent()
        
        # Get conversation history from database
        conversation_history = await get_conversation_history(db, instance_name, from_phone)
        
        # Process the message (agent will load configuration from database)
        result = await agent.process_message(
            message=message_content,
            customer_phone=from_phone,
            instance_name=instance_name,
            conversation_history=conversation_history,
            db_session=db
        )
        
        # Extract response from result (LangGraph returns dict)
        agent_response = result.get("response", "No response generated")
        logger.info(f"[{request_id}] 🤖 Agent response: '{agent_response}'")
        
        # Send the response back through WhatsApp
        if agent_response:
            send_result = await evolution_service.send_message(
                instance_name=instance_name,
                to=from_phone,
                message=agent_response
            )
            
            if send_result["success"]:
                logger.info(f"[{request_id}] ✅ Response sent successfully")
            else:
                logger.error(f"[{request_id}] ❌ Failed to send response: {send_result['error']}")
        
        # Handle appointment booking if needed
        if result.get("should_book_appointment") and result.get("appointment_details"):
            await handle_appointment_booking(
                instance_name,
                from_phone,
                result.get("appointment_details"),
                request_id
            )
        
        # Store message and response in database
        # Note: This is simplified - in production you'd want proper transaction handling
        await store_conversation_message(
            db,
            instance_name,
            from_phone,
            message_content,
            agent_response,
            request_id
        )
        
    except Exception as e:
        logger.error(f"[{request_id}] Error handling incoming message: {e}")
        
        # Send fallback message
        try:
            fallback_message = "Disculpa, estoy teniendo problemas técnicos en este momento. Por favor, intenta más tarde."
            await evolution_service.send_message(
                instance_name=webhook_data.get("instance", ""),
                to=webhook_data.get("data", {}).get("messages", [{}])[0].get("key", {}).get("remoteJid", "").split('@')[0],
                message=fallback_message
            )
        except:
            logger.error(f"[{request_id}] Failed to send fallback message")


async def handle_qr_code_update(
    webhook_data: Dict[str, Any],
    request_id: str,
    db: AsyncSession
):
    """
    Handle QR code updates for WhatsApp instances.
    
    Args:
        webhook_data: Webhook data containing QR code info
        request_id: Request identifier for logging
        db: Database session
    """
    try:
        instance_name = webhook_data.get("instance")
        data = webhook_data.get("data", {})
        qr_code = data.get("qr")
        
        logger.info(f"[{request_id}] QR code updated for instance: {instance_name}")
        
        # Store QR code in database for frontend to retrieve
        # Note: This is simplified - in production you'd update the Instance record
        
    except Exception as e:
        logger.error(f"[{request_id}] Error handling QR code update: {e}")


async def handle_appointment_booking(
    instance_name: str,
    customer_phone: str,
    appointment_details: Dict[str, Any],
    request_id: str
):
    """
    Handle appointment booking through Google Calendar.
    
    Args:
        instance_name: WhatsApp instance name
        customer_phone: Customer's phone number
        appointment_details: Appointment details from the agent
        request_id: Request identifier for logging
    """
    try:
        logger.info(f"[{request_id}] 📅 Attempting to book appointment for {customer_phone}")
        
        # Get Google Calendar tokens for this instance
        # Note: In production, you'd query the database for the agent config and tokens
        
        # For now, we'll log the booking attempt
        logger.info(f"[{request_id}] Appointment details: {appointment_details}")
        
        # TODO: Implement actual Google Calendar booking
        # 1. Get agent config and Google tokens from database
        # 2. Create calendar event using calendar_service
        # 3. Send confirmation message to customer
        # 4. Store booking in database
        
        confirmation_message = f"✅ ¡Cita confirmada! Te esperamos el {appointment_details.get('start_time', 'fecha programada')}. Recibirás una confirmación por email."
        
        await evolution_service.send_message(
            instance_name=instance_name,
            to=customer_phone,
            message=confirmation_message
        )
        
        logger.info(f"[{request_id}] 📅 Booking confirmation sent")
        
    except Exception as e:
        logger.error(f"[{request_id}] Error handling appointment booking: {e}")


async def get_conversation_history(
    db: AsyncSession,
    instance_name: str,
    customer_phone: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """Get conversation history for a customer from the database."""
    try:
        from sqlalchemy import select, and_
        from app.models.database import Instance, Conversation, Message
        
        # Get instance ID
        instance_result = await db.execute(
            select(Instance).where(Instance.instance_name == instance_name)
        )
        instance = instance_result.scalar_one_or_none()
        
        if not instance:
            return []
        
        # Get conversation
        conversation_result = await db.execute(
            select(Conversation).where(
                and_(
                    Conversation.instance_id == instance.id,
                    Conversation.customer_phone == customer_phone
                )
            )
        )
        conversation = conversation_result.scalar_one_or_none()
        
        if not conversation:
            return []
        
        # Get recent messages
        messages_result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = messages_result.scalars().all()
        
        # Convert to conversation format
        conversation_history = []
        for message in reversed(messages):  # Reverse to get chronological order
            conversation_history.append({
                "role": "human" if message.direction == "incoming" else "assistant",
                "content": message.content,
                "timestamp": message.created_at.isoformat()
            })
        
        return conversation_history
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return []

async def store_conversation_message(
    db: AsyncSession,
    instance_name: str,
    customer_phone: str,
    incoming_message: str,
    agent_response: str,
    request_id: str
):
    """
    Store conversation messages in the database.
    
    Args:
        db: Database session
        instance_name: WhatsApp instance name
        customer_phone: Customer's phone number
        incoming_message: The customer's message
        agent_response: The agent's response
        request_id: Request identifier for logging
    """
    try:
        logger.info(f"[{request_id}] 💾 Storing conversation for {customer_phone}")
        
        from sqlalchemy import select, insert
        from sqlalchemy.dialects.postgresql import insert as pg_insert
        import uuid
        from datetime import datetime
        
        # Clean phone number (remove @s.whatsapp.net)
        clean_phone = customer_phone.split('@')[0] if '@' in customer_phone else customer_phone
        
        # 1. Find or create Instance record
        instance_result = await db.execute(
            select(Instance).where(Instance.instance_name == instance_name)
        )
        instance = instance_result.scalar_one_or_none()
        
        if not instance:
            logger.warning(f"[{request_id}] Instance {instance_name} not found, creating...")
            instance_id = str(uuid.uuid4())
            await db.execute(
                insert(Instance).values(
                    id=instance_id,
                    instance_name=instance_name,
                    status="connected",
                    created_at=datetime.now()
                )
            )
        else:
            instance_id = instance.id
            
        # 2. Find or create Conversation record
        conversation_result = await db.execute(
            select(Conversation).where(
                Conversation.instance_id == instance_id,
                Conversation.customer_phone == clean_phone
            )
        )
        conversation = conversation_result.scalar_one_or_none()
        
        if not conversation:
            logger.info(f"[{request_id}] Creating new conversation for {clean_phone}")
            conversation_id = str(uuid.uuid4())
            await db.execute(
                insert(Conversation).values(
                    id=conversation_id,
                    instance_id=instance_id,
                    customer_phone=clean_phone,
                    status="active",
                    last_message_at=datetime.now(),
                    created_at=datetime.now()
                )
            )
        else:
            conversation_id = conversation.id
            # Update last_message_at
            await db.execute(
                Conversation.__table__.update()
                .where(Conversation.id == conversation_id)
                .values(last_message_at=datetime.now())
            )
        
        # 3. Create Message records for both incoming and outgoing messages
        now = datetime.now()
        
        # Incoming message
        incoming_message_id = str(uuid.uuid4())
        await db.execute(
            insert(Message).values(
                id=incoming_message_id,
                conversation_id=conversation_id,
                content=incoming_message,
                message_type="text",
                direction="incoming",
                sender_phone=clean_phone,
                processed=True,
                processed_at=now,
                created_at=now
            )
        )
        
        # Outgoing message (agent response)
        outgoing_message_id = str(uuid.uuid4())
        await db.execute(
            insert(Message).values(
                id=outgoing_message_id,
                conversation_id=conversation_id,
                content=agent_response,
                message_type="text",
                direction="outgoing",
                sender_phone="agent",
                processed=True,
                processed_at=now,
                created_at=now
            )
        )
        
        # Commit the transaction
        await db.commit()
        
        logger.info(f"[{request_id}] ✅ Successfully stored conversation and messages in Supabase")
        logger.info(f"[{request_id}] 📊 Conversation ID: {conversation_id}")
        logger.info(f"[{request_id}] 📨 Messages: {incoming_message_id} (in), {outgoing_message_id} (out)")
        
    except Exception as e:
        logger.error(f"[{request_id}] ❌ Error storing conversation: {e}")
        await db.rollback()


@router.get("/evolution/test")
async def test_evolution_webhook():
    """Test endpoint to verify webhook is working."""
    return {
        "status": "Evolution webhook endpoint is ready",
        "timestamp": datetime.now().isoformat(),
        "events": ["connection.update", "messages.upsert", "qrcode.updated"]
    }

