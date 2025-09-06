"""
Conversational agent using LangGraph for intelligent WhatsApp interactions.
Handles customer conversations, intent detection, and appointment booking.
"""

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import re
import logging
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class ConversationState(BaseModel):
    """State of the conversation maintained throughout the interaction."""
    
    # Message history
    messages: List[Dict[str, Any]] = []
    
    # Customer information
    customer_phone: str
    customer_name: Optional[str] = None
    
    # Agent configuration
    agent_name: str
    agent_purpose: str
    agent_behavior: str
    working_hours_start: str = "09:00"
    working_hours_end: str = "18:00"
    
    # Conversation context
    intent: Optional[Literal["greeting", "booking", "info", "confirmation", "unknown"]] = None
    booking_data: Dict[str, Any] = {}
    
    # Final response
    response: Optional[str] = None
    should_book_appointment: bool = False
    appointment_details: Dict[str, Any] = {}


class ConversationAgent:
    """
    LangGraph-based conversational agent for handling WhatsApp conversations.
    Uses OpenAI GPT models for natural language understanding and generation.
    """
    
    def __init__(self):
        """Initialize the conversation agent with LangGraph workflow."""
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Use GPT-4o-mini for cost efficiency
            temperature=0.3,  # Low temperature for consistent responses
            api_key=settings.OPENAI_API_KEY
        )
        
        # Build the conversation workflow graph
        self.workflow = self._build_workflow()
        
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow for conversation handling.
        
        Workflow steps:
        1. Check working hours
        2. Detect intent from user message
        3. Route to appropriate handler (greeting, booking, info, etc.)
        4. Generate response
        5. Determine if appointment booking is needed
        """
        workflow = StateGraph(ConversationState)
        
        # Add nodes for each step in the conversation
        workflow.add_node("check_working_hours", self._check_working_hours)
        workflow.add_node("detect_intent", self._detect_intent)
        workflow.add_node("handle_greeting", self._handle_greeting)
        workflow.add_node("handle_booking", self._handle_booking)
        workflow.add_node("handle_info_request", self._handle_info_request)
        workflow.add_node("handle_unknown", self._handle_unknown)
        workflow.add_node("generate_response", self._generate_response)
        
        # Set entry point
        workflow.set_entry_point("check_working_hours")
        
        # Add conditional edges based on working hours and intent
        workflow.add_conditional_edges(
            "check_working_hours",
            self._route_working_hours,
            {
                "within_hours": "detect_intent",
                "outside_hours": "generate_response"
            }
        )
        
        workflow.add_conditional_edges(
            "detect_intent",
            self._route_intent,
            {
                "greeting": "handle_greeting",
                "booking": "handle_booking", 
                "info": "handle_info_request",
                "unknown": "handle_unknown"
            }
        )
        
        # All handlers lead to response generation
        workflow.add_edge("handle_greeting", "generate_response")
        workflow.add_edge("handle_booking", "generate_response")
        workflow.add_edge("handle_info_request", "generate_response")
        workflow.add_edge("handle_unknown", "generate_response")
        
        # End after generating response
        workflow.add_edge("generate_response", END)
        
        return workflow.compile()
    
    async def _load_agent_config(self, instance_name: str, db_session) -> Dict[str, Any]:
        """Load agent configuration from database for the given instance."""
        try:
            if not db_session:
                # Fallback to default configuration if no database session
                return {
                    "agent_name": "Sofia",
                    "agent_purpose": "Soy un asistente virtual que ayuda a agendar citas para nuestro consultorio dental.",
                    "agent_behavior": "Soy amable, profesional y empática. Ayudo a los clientes a agendar citas y respondo preguntas sobre nuestros servicios.",
                    "working_hours_start": "09:00",
                    "working_hours_end": "18:00",
                    "timezone": "America/Bogota",
                    "language": "es"
                }
            
            from sqlalchemy import select
            from app.models.database import AgentConfig
            
            result = await db_session.execute(
                select(AgentConfig).where(AgentConfig.instance_name == instance_name)
            )
            config = result.scalar_one_or_none()
            
            if config:
                return {
                    "agent_name": config.agent_name,
                    "agent_purpose": config.agent_purpose,
                    "agent_behavior": config.agent_behavior,
                    "working_hours_start": config.working_hours_start,
                    "working_hours_end": config.working_hours_end,
                    "timezone": config.timezone,
                    "language": config.language,
                    "greeting_message": config.greeting_message,
                    "fallback_message": config.fallback_message,
                    "booking_instructions": config.booking_instructions,
                    "custom_prompts": config.custom_prompts or {}
                }
            else:
                # Return default configuration if no config found
                return {
                    "agent_name": "Sofia",
                    "agent_purpose": "Soy un asistente virtual que ayuda a agendar citas para nuestro consultorio dental.",
                    "agent_behavior": "Soy amable, profesional y empática. Ayudo a los clientes a agendar citas y respondo preguntas sobre nuestros servicios.",
                    "working_hours_start": "09:00",
                    "working_hours_end": "18:00",
                    "timezone": "America/Bogota",
                    "language": "es"
                }
                
        except Exception as e:
            logger.error(f"Error loading agent configuration: {e}")
            # Return default configuration on error
            return {
                "agent_name": "Sofia",
                "agent_purpose": "Soy un asistente virtual que ayuda a agendar citas para nuestro consultorio dental.",
                "agent_behavior": "Soy amable, profesional y empática. Ayudo a los clientes a agendar citas y respondo preguntas sobre nuestros servicios.",
                "working_hours_start": "09:00",
                "working_hours_end": "18:00",
                "timezone": "America/Bogota",
                "language": "es"
            }
    
    async def process_message(
        self, 
        message: str, 
        customer_phone: str,
        instance_name: str,
        conversation_history: List[Dict[str, Any]] = None,
        db_session = None
    ) -> ConversationState:
        """
        Process an incoming message and generate an appropriate response.
        
        Args:
            message: The customer's message
            customer_phone: Customer's phone number
            instance_name: WhatsApp instance name
            conversation_history: Previous messages in the conversation
            db_session: Database session for loading configuration
            
        Returns:
            ConversationState with the agent's response and any booking details
        """
        # Load agent configuration from database
        agent_config = await self._load_agent_config(instance_name, db_session)
        
        # Initialize conversation state
        initial_state = ConversationState(
            messages=conversation_history or [],
            customer_phone=customer_phone,
            agent_name=agent_config.get("agent_name", "Assistant"),
            agent_purpose=agent_config.get("agent_purpose", ""),
            agent_behavior=agent_config.get("agent_behavior", ""),
            working_hours_start=agent_config.get("working_hours_start", "09:00"),
            working_hours_end=agent_config.get("working_hours_end", "18:00")
        )
        
        # Add the current message to the conversation
        initial_state.messages.append({
            "role": "human",
            "content": message,
            "timestamp": datetime.now().isoformat()
        })
        
        try:
            # Run the workflow
            final_state = await self.workflow.ainvoke(initial_state)
            logger.info(f"Agent processed message successfully for {customer_phone}")
            return final_state
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return fallback response
            initial_state.response = "I'm sorry, I'm having technical difficulties right now. Please try again later or contact us directly."
            return initial_state
    
    def _check_working_hours(self, state: ConversationState) -> ConversationState:
        """Check if the current time is within working hours."""
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        
        # Simple time comparison (assumes same timezone)
        if state.working_hours_start <= current_time <= state.working_hours_end:
            # Don't set intent here - let detect_intent handle it
            pass
        else:
            state.response = self._generate_out_of_hours_message(state)
            
        return state
    
    def _detect_intent(self, state: ConversationState) -> ConversationState:
        """Detect the intent of the user's message using LLM."""
        last_message = state.messages[-1]["content"].lower()
        
        # Create prompt for intent detection
        intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for a conversational agent. 
            Classify the user's message into one of these intents:
            - greeting: greetings, hello, hi, good morning, etc.
            - booking: wants to schedule/book an appointment, cita, agendar, reservar
            - info: asking for information, prices, services, location, hours
            - unknown: anything else
            
            Respond with only the intent name."""),
            ("human", "{message}")
        ])
        
        try:
            response = self.llm.invoke(intent_prompt.format_messages(message=last_message))
            detected_intent = response.content.strip().lower()
            
            # Validate intent
            valid_intents = ["greeting", "booking", "info", "unknown"]
            state.intent = detected_intent if detected_intent in valid_intents else "unknown"
            
        except Exception as e:
            logger.error(f"Error detecting intent: {e}")
            state.intent = "unknown"
            
        return state
    
    def _handle_greeting(self, state: ConversationState) -> ConversationState:
        """Handle greeting messages."""
        greeting_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are {state.agent_name}, a helpful assistant.
            Business purpose: {state.agent_purpose}
            Behavior: {state.agent_behavior}
            
            The user has greeted you. Respond warmly and offer help with:
            - Scheduling appointments
            - Information about services
            - Any questions they might have
            
            Keep it friendly, professional, and concise. Include your name in the response."""),
            ("human", "{message}")
        ])
        
        try:
            last_message = state.messages[-1]["content"]
            response = self.llm.invoke(greeting_prompt.format_messages(message=last_message))
            state.response = response.content
            
        except Exception as e:
            logger.error(f"Error handling greeting: {e}")
            state.response = f"Hello! I'm {state.agent_name}. How can I help you today?"
            
        return state
    
    def _handle_booking(self, state: ConversationState) -> ConversationState:
        """Handle appointment booking requests."""
        last_message = state.messages[-1]["content"]
        
        # Extract date and time from message using regex
        date_pattern = r'(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})'
        time_pattern = r'(\d{1,2}):(\d{2})'
        
        date_match = re.search(date_pattern, last_message)
        time_match = re.search(time_pattern, last_message)
        
        if date_match and time_match:
            # User provided date and time
            day, month, year = date_match.groups()
            hour, minute = time_match.groups()
            
            try:
                # Validate and create datetime
                appointment_datetime = datetime(
                    int(year), int(month), int(day), 
                    int(hour), int(minute)
                )
                
                if appointment_datetime > datetime.now():
                    # Valid future date
                    state.should_book_appointment = True
                    state.appointment_details = {
                        "title": f"Appointment with {state.agent_name}",
                        "start_time": appointment_datetime.isoformat(),
                        "end_time": (appointment_datetime + timedelta(hours=1)).isoformat(),
                        "customer_phone": state.customer_phone,
                        "customer_name": state.customer_name
                    }
                    
                    state.response = f"Perfect! I have availability on {day}/{month}/{year} at {hour}:{minute}. Could you please confirm your full name for the appointment?"
                else:
                    state.response = "The date you selected is in the past. Please choose a future date and time."
                    
            except ValueError:
                state.response = "The date or time format seems incorrect. Please use DD/MM/YYYY and HH:MM format."
                
        else:
            # Ask for date and time
            booking_prompt = ChatPromptTemplate.from_messages([
                ("system", f"""You are {state.agent_name} helping with appointment booking.
                Working hours: {state.working_hours_start} to {state.working_hours_end}
                
                The user wants to book an appointment but hasn't provided date/time.
                Ask them to specify the date and time in DD/MM/YYYY and HH:MM format.
                Mention your available hours and be helpful."""),
                ("human", "{message}")
            ])
            
            try:
                response = self.llm.invoke(booking_prompt.format_messages(message=last_message))
                state.response = response.content
            except Exception as e:
                logger.error(f"Error handling booking: {e}")
                state.response = f"I'd be happy to help you schedule an appointment! Please let me know your preferred date and time. I'm available from {state.working_hours_start} to {state.working_hours_end}."
        
        return state
    
    def _handle_info_request(self, state: ConversationState) -> ConversationState:
        """Handle information requests about the business."""
        info_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are {state.agent_name}, providing information about the business.
            Business purpose: {state.agent_purpose}
            Behavior: {state.agent_behavior}
            Working hours: {state.working_hours_start} to {state.working_hours_end}
            
            Answer the user's question based on the business information provided.
            If you don't have specific information, offer to help schedule an appointment or suggest contacting directly.
            Always be helpful and professional."""),
            ("human", "{message}")
        ])
        
        try:
            last_message = state.messages[-1]["content"]
            response = self.llm.invoke(info_prompt.format_messages(message=last_message))
            state.response = response.content
            
        except Exception as e:
            logger.error(f"Error handling info request: {e}")
            state.response = "I'd be happy to help with information about our services. Would you like to schedule an appointment to discuss your needs?"
            
        return state
    
    def _handle_unknown(self, state: ConversationState) -> ConversationState:
        """Handle unknown or unclear messages."""
        unknown_prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are {state.agent_name}, a helpful assistant.
            The user's message is unclear or doesn't fit standard categories.
            
            Politely ask for clarification and offer the main services:
            - Scheduling appointments
            - Information about services
            - Answering questions
            
            Be friendly and helpful."""),
            ("human", "{message}")
        ])
        
        try:
            last_message = state.messages[-1]["content"]
            response = self.llm.invoke(unknown_prompt.format_messages(message=last_message))
            state.response = response.content
            
        except Exception as e:
            logger.error(f"Error handling unknown message: {e}")
            state.response = "I'm not sure I understand. Could you please clarify? I can help you schedule appointments, provide information about our services, or answer any questions you might have."
            
        return state
    
    def _generate_response(self, state: ConversationState) -> ConversationState:
        """Generate the final response (if not already set)."""
        if not state.response:
            state.response = "Thank you for your message. How can I assist you today?"
        
        # Add the response to message history
        state.messages.append({
            "role": "assistant",
            "content": state.response,
            "timestamp": datetime.now().isoformat()
        })
        
        return state
    
    def _generate_out_of_hours_message(self, state: ConversationState) -> str:
        """Generate an out-of-hours message."""
        return f"Hello! I'm {state.agent_name}. We're currently outside our business hours ({state.working_hours_start} - {state.working_hours_end}). I'll respond during our next business day. Thank you for your patience!"
    
    def _route_working_hours(self, state: ConversationState) -> str:
        """Route based on working hours check."""
        # If response is already set (out of hours), go to generate_response
        if state.response:
            return "outside_hours"
        else:
            return "within_hours"
    
    def _route_intent(self, state: ConversationState) -> str:
        """Route based on detected intent."""
        return state.intent or "unknown"

