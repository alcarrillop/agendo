"""
Service for Google Calendar integration.
Handles OAuth authentication, event creation, and availability checking.
"""

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import logging
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class GoogleCalendarService:
    """
    Service class for Google Calendar integration.
    Handles authentication, event creation, and calendar operations.
    """
    
    # Required scopes for Google Calendar access
    SCOPES = [
        'https://www.googleapis.com/auth/calendar',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self):
        """Initialize the Google Calendar service."""
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI or f"{settings.BACKEND_CORS_ORIGINS[0]}/api/v1/auth/google/callback"
        
        if not all([self.client_id, self.client_secret]):
            logger.warning("Google Calendar credentials not fully configured")
    
    def create_oauth_flow(self) -> Flow:
        """
        Create OAuth2 flow for Google Calendar authentication.
        
        Returns:
            Google OAuth2 Flow object
        """
        if not all([self.client_id, self.client_secret]):
            raise ValueError("Google Calendar credentials not configured")
            
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        return flow
    
    def get_authorization_url(self, state: str = None) -> Tuple[str, str]:
        """
        Generate Google OAuth authorization URL.
        
        Args:
            state: Optional state parameter for OAuth flow
            
        Returns:
            Tuple of (authorization_url, state)
        """
        flow = self.create_oauth_flow()
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent screen to get refresh token
        )
        
        return authorization_url, state
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access and refresh tokens.
        
        Args:
            code: Authorization code from Google OAuth callback
            
        Returns:
            Dict containing token information and user details
        """
        try:
            flow = self.create_oauth_flow()
            flow.fetch_token(code=code)
            
            credentials = flow.credentials
            
            # Get user information
            user_info = await self._get_user_info(credentials)
            
            return {
                "success": True,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expires_at": credentials.expiry,
                "user_email": user_info.get("email"),
                "user_name": user_info.get("name"),
                "user_info": user_info
            }
            
        except Exception as e:
            logger.error(f"Error exchanging code for tokens: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_user_info(self, credentials: Credentials) -> Dict[str, Any]:
        """
        Get user information from Google API.
        
        Args:
            credentials: Google OAuth2 credentials
            
        Returns:
            Dict containing user information
        """
        try:
            service = build('oauth2', 'v2', credentials=credentials)
            user_info = service.userinfo().get().execute()
            return user_info
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {}
    
    def _create_credentials(self, token_data: Dict[str, Any]) -> Credentials:
        """
        Create Google credentials object from stored token data.
        
        Args:
            token_data: Dict containing access token, refresh token, etc.
            
        Returns:
            Google Credentials object
        """
        return Credentials(
            token=token_data["access_token"],
            refresh_token=token_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.SCOPES
        )
    
    async def create_event(
        self,
        token_data: Dict[str, Any],
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendee_email: Optional[str] = None,
        timezone: str = "America/Bogota"
    ) -> Dict[str, Any]:
        """
        Create a new calendar event.
        
        Args:
            token_data: Google OAuth token data
            title: Event title
            description: Event description
            start_time: Event start datetime
            end_time: Event end datetime
            attendee_email: Optional attendee email
            timezone: Event timezone
            
        Returns:
            Dict containing the created event information
        """
        try:
            credentials = self._create_credentials(token_data)
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            service = build('calendar', 'v3', credentials=credentials)
            
            # Create event object
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': timezone,
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},  # 1 day before
                        {'method': 'popup', 'minutes': 30},       # 30 minutes before
                    ],
                },
            }
            
            # Add attendee if provided
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            # Create the event
            created_event = service.events().insert(
                calendarId='primary',
                body=event,
                sendUpdates='all'  # Send email invitations
            ).execute()
            
            logger.info(f"Calendar event created: {created_event['id']}")
            
            return {
                "success": True,
                "event_id": created_event['id'],
                "event_url": created_event.get('htmlLink'),
                "event": {
                    "id": created_event['id'],
                    "title": created_event['summary'],
                    "start": created_event['start']['dateTime'],
                    "end": created_event['end']['dateTime'],
                    "description": created_event.get('description', ''),
                    "url": created_event.get('htmlLink')
                }
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            return {
                "success": False,
                "error": f"Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def check_availability(
        self,
        token_data: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
        timezone: str = "America/Bogota"
    ) -> Dict[str, Any]:
        """
        Check availability for a given time slot.
        
        Args:
            token_data: Google OAuth token data
            start_time: Start time to check
            end_time: End time to check
            timezone: Timezone for the check
            
        Returns:
            Dict containing availability information
        """
        try:
            credentials = self._create_credentials(token_data)
            
            # Refresh token if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            service = build('calendar', 'v3', credentials=credentials)
            
            # Get events in the time range
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat() + 'Z',
                timeMax=end_time.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check for conflicts
            is_available = len(events) == 0
            
            return {
                "success": True,
                "is_available": is_available,
                "conflicting_events": [
                    {
                        "id": event['id'],
                        "title": event.get('summary', 'No title'),
                        "start": event['start'].get('dateTime', event['start'].get('date')),
                        "end": event['end'].get('dateTime', event['end'].get('date'))
                    }
                    for event in events
                ]
            }
            
        except HttpError as e:
            logger.error(f"Google Calendar API error checking availability: {e}")
            return {
                "success": False,
                "error": f"Calendar API error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error checking availability: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_daily_availability(
        self,
        token_data: Dict[str, Any],
        date: datetime,
        working_hours_start: str = "09:00",
        working_hours_end: str = "18:00",
        slot_duration_minutes: int = 60,
        timezone: str = "America/Bogota"
    ) -> Dict[str, Any]:
        """
        Get available time slots for a specific date.
        
        Args:
            token_data: Google OAuth token data
            date: Date to check (time will be ignored)
            working_hours_start: Start of working hours (HH:MM)
            working_hours_end: End of working hours (HH:MM)
            slot_duration_minutes: Duration of each slot in minutes
            timezone: Timezone for the check
            
        Returns:
            Dict containing available time slots
        """
        try:
            # Create start and end datetime for the day
            start_hour, start_minute = map(int, working_hours_start.split(':'))
            end_hour, end_minute = map(int, working_hours_end.split(':'))
            
            day_start = date.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
            day_end = date.replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
            
            # Get busy periods for the day
            credentials = self._create_credentials(token_data)
            
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            service = build('calendar', 'v3', credentials=credentials)
            
            events_result = service.events().list(
                calendarId='primary',
                timeMin=day_start.isoformat() + 'Z',
                timeMax=day_end.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            busy_periods = []
            for event in events_result.get('items', []):
                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')
                
                if start and end:
                    busy_periods.append({
                        'start': datetime.fromisoformat(start.replace('Z', '+00:00')),
                        'end': datetime.fromisoformat(end.replace('Z', '+00:00'))
                    })
            
            # Generate available slots
            available_slots = []
            current_time = day_start
            slot_duration = timedelta(minutes=slot_duration_minutes)
            
            while current_time + slot_duration <= day_end:
                slot_end = current_time + slot_duration
                
                # Check if this slot conflicts with any busy period
                is_free = True
                for busy in busy_periods:
                    if (current_time < busy['end'] and slot_end > busy['start']):
                        is_free = False
                        break
                
                if is_free:
                    available_slots.append({
                        'start': current_time.isoformat(),
                        'end': slot_end.isoformat(),
                        'start_time': current_time.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M')
                    })
                
                current_time += slot_duration
            
            return {
                "success": True,
                "date": date.strftime('%Y-%m-%d'),
                "available_slots": available_slots,
                "total_slots": len(available_slots),
                "busy_periods": [
                    {
                        'start': busy['start'].isoformat(),
                        'end': busy['end'].isoformat()
                    }
                    for busy in busy_periods
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting daily availability: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global service instance
calendar_service = GoogleCalendarService()

