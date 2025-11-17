"""
Calendar Integration Module using MCP (Model Context Protocol)
Handles Google Calendar authentication and event retrieval via the MCP SDK.

Citations:
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- MCP Documentation: https://modelcontextprotocol.io/
- Assignment Requirement: Use MCP SDK for auth and data fetching.
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta

# ADDED: MCP SDK imports
# We assume the library provides a main client and specific exceptions
try:
    from mcp import ContextProtocol
    from mcp.exceptions import McpAuthenticationError, McpApiError
except ImportError:
    print("="*60)
    print("ERROR: 'mcp' library not found. Please install with: pip install mcp")
    print("="*60)
    ContextProtocol = None
    McpAuthenticationError = Exception
    McpApiError = Exception

# ADDED: Import config from your settings file
from src.config.settings import config

# REMOVED: All Google library imports:
# - google.auth.transport.requests
# - google.oauth2.credentials
# - google_auth_oauthlib.flow
# - googleapiclient.discovery
# - googleapiclient.errors
# - pickle


class CalendarIntegration:
    """
    Manages Google Calendar integration using MCP standards.
    Handles OAuth authentication, token management, and calendar operations
    via the MCP Python SDK.
    """
    
    def __init__(self):
        """
        Initialize Calendar Integration.
        
        REMOVED: credentials_file and token_file. MCP SDK handles this.
        """
        if not ContextProtocol:
            raise ImportError("MCP SDK is not installed or failed to import.")
            
        # ADDED: Get MCP server URL from config
        self.mcp_server_url = config.MCP_SERVER_URL
        self.client = None  # This will be the authenticated ContextProtocol client
        self.service = None # chatbot.py checks for this, so we'll mirror client to it
        
        print(f"🗓️  Calendar Integration initialized (MCP Mode). Server: {self.mcp_server_url}")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API using the MCP SDK.
        This replaces the direct Google OAuth2 flow.
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Citation: MCP SDK Authentication Guide
        """
        try:
            print("🔐 Starting MCP OAuth authentication flow...")
            
            # This is an assumed authentication method from the MCP SDK.
            # The SDK will use the provided credentials to initiate
            # an OAuth flow for its Google Calendar provider.
            # You MUST check the MCP SDK documentation for the exact method.
            self.client = ContextProtocol.authenticate_google(
                server_url=self.mcp_server_url,
                client_id=config.GOOGLE_CLIENT_ID,
                client_secret=config.GOOGLE_CLIENT_SECRET,
                redirect_uri=config.GOOGLE_REDIRECT_URI,
                scopes=config.GOOGLE_SCOPES
            )
            
            if self.client and self.client.is_authenticated():
                # The chatbot.py file checks for 'self.calendar.service'
                # We set it here to maintain that interface.
                self.service = self.client 
                print("✅ Successfully authenticated with Google Calendar via MCP")
                return True
            else:
                self.service = None
                print("❌ MCP Authentication failed. Client not authenticated.")
                return False
            
        except McpAuthenticationError as e:
            print(f"❌ MCP Authentication error: {e}")
            self.service = None
            return False
        except Exception as e:
            # Catch other errors, e.g., config not found
            print(f"❌ General authentication error: {e}")
            self.service = None
            return False
    
    def get_calendar_list(self) -> List[Dict[str, Any]]:
        """
        Retrieve list of all calendars using the MCP client.
        
        Returns:
            list: List of calendar objects
        """
        try:
            if not self.service:
                print("❌ MCP Service not initialized. Please authenticate first.")
                return []
            
            # Assumed SDK method:
            calendar_list = self.service.calendar.list_calendars()
            calendars = calendar_list.get('items', [])
            
            print(f"✅ Retrieved {len(calendars)} calendars via MCP")
            return calendars
            
        except McpApiError as error:
            print(f"❌ Error retrieving MCP calendar list: {error}")
            return []
    
    def get_events(
        self,
        calendar_id: str = 'primary',
        time_min: Optional[datetime] = None,
        time_max: Optional[datetime] = None,
        max_results: int = 10,
        single_events: bool = True,
        order_by: str = 'startTime'
    ) -> List[Dict[str, Any]]:
        """
        Retrieve calendar events using the MCP client.
        
        Args:
            (Args are the same as the original)
            
        Returns:
            list: List of event objects
        """
        try:
            if not self.service:
                print("❌ MCP Service not initialized. Please authenticate first.")
                return []
            
            # Set default time range if not provided (logic is unchanged)
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=7)
            
            # Convert datetime to RFC3339 format (logic is unchanged)
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'
            
            # REPLACED: Direct Google API call
            # This is the new call using the assumed MCP SDK interface
            events_result = self.service.calendar.get_events(
                calendar_id=calendar_id,
                time_min=time_min_str,
                time_max=time_max_str,
                max_results=max_results,
                single_events=single_events,
                order_by=order_by
            )
            
            events = events_result.get('items', [])
            print(f"✅ Retrieved {len(events)} events via MCP")
            return events
            
        except McpApiError as error:
            print(f"❌ Error retrieving MCP events: {error}")
            return []
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """
        Get all events for today. (Logic is unchanged)
        """
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.get_events(time_min=start_of_day, time_max=end_of_day)
    
    def get_week_events(self) -> List[Dict[str, Any]]:
        """
        Get all events for the current week. (Logic is unchanged)
        """
        now = datetime.utcnow()
        end_of_week = now + timedelta(days=7)
        
        return self.get_events(time_min=now, time_max=end_of_week, max_results=50)
    
    def format_event(self, event: Dict[str, Any]) -> str:
        """
        Format a calendar event into a readable string.
        
        NOTE: This function is unchanged, but you MUST verify that
        the event object structure returned by the MCP SDK
        matches the Google API event structure. If not, you will
        need to adjust the keys (e.g., 'summary', 'start', 'dateTime').
        """
        try:
            summary = event.get('summary', 'No Title')
            start = event.get('start', {})
            end = event.get('end', {})
            location = event.get('location', 'No location')
            description = event.get('description', 'No description')
            
            if 'dateTime' in start:
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                time_str = f"{start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}"
            else:
                start_date = start.get('date', 'N/A')
                time_str = f"All day ({start_date})"
            
            formatted = f"📅 **{summary}**\n"
            formatted += f"   ⏰ {time_str}\n"
            
            if location != 'No location':
                formatted += f"   📍 {location}\n"
            
            if description != 'No description' and description:
                desc = description[:100] + "..." if len(description) > 100 else description
                formatted += f"   📝 {desc}\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting event: {e}"
    
    def format_events_list(self, events: List[Dict[str, Any]]) -> str:
        """
        Format a list of events into a readable string. (Logic is unchanged)
        """
        if not events:
            return "No upcoming events found."
        
        formatted = f"Found {len(events)} event(s):\n\n"
        for i, event in enumerate(events, 1):
            formatted += f"{i}. {self.format_event(event)}\n"
        
        return formatted
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for events matching a query string using MCP client.
        """
        try:
            if not self.service:
                print("❌ MCP Service not initialized. Please authenticate first.")
                return []
            
            now = datetime.utcnow().isoformat() + 'Z'
            
            # Assumed SDK method:
            events_result = self.service.calendar.search_events(
                calendar_id='primary',
                time_min=now,
                max_results=max_results,
                query=query,
                single_events=True,
                order_by='startTime'
            )
            
            events = events_result.get('items', [])
            print(f"✅ Found {len(events)} events matching '{query}' via MCP")
            return events
            
        except McpApiError as error:
            print(f"❌ Error searching MCP events: {error}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Initialize calendar integration
    calendar = CalendarIntegration()
    
    # Test 1: Authentication
    print("\n--- Test 1: MCP Authentication ---")
    if not calendar.authenticate():
        print("MCP Authentication failed!")
        exit(1)
    
    print("MCP Authentication successful!")
    
    # Test 2: Get calendar list
    print("\n--- Test 2: MCP Calendar List ---")
    calendars = calendar.get_calendar_list()
    for cal in calendars[:3]:  # Show first 3
        print(f"- {cal.get('summary', 'N/A')}")
    
    # Test 3: Get today's events
    print("\n--- Test 3: MCP Today's Events ---")
    today_events = calendar.get_today_events()
    print(calendar.format_events_list(today_events))
    
    # Test 4: Search events
    print("\n--- Test 4: MCP Search Events ---")
    search_results = calendar.search_events("meeting")
    print(calendar.format_events_list(search_results))
