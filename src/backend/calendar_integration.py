"""
Calendar Integration Module using MCP (Model Context Protocol)
Handles Google Calendar authentication and event retrieval.

Citations:
- MCP Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Google Calendar API: https://developers.google.com/calendar/api/v3/reference
- OAuth2 Authentication: https://developers.google.com/identity/protocols/oauth2
"""

import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import pickle
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class CalendarIntegration:
    """
    Manages Google Calendar integration using MCP standards.
    Handles OAuth authentication, token management, and calendar operations.
    """
    
    # Citation: Google Calendar API scopes
    # https://developers.google.com/calendar/api/guides/auth
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    
    def __init__(self, credentials_file: str = 'credentials.json', token_file: str = 'token.pickle'):
        """
        Initialize Calendar Integration.
        
        Args:
            credentials_file (str): Path to Google OAuth credentials JSON
            token_file (str): Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.creds = None
        self.service = None
        
        print("🗓️  Calendar Integration initialized")
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar API using OAuth 2.0.
        Implements secure token handling and refresh logic.
        
        Returns:
            bool: True if authentication successful, False otherwise
            
        Citation: Google OAuth2 flow - https://developers.google.com/identity/protocols/oauth2
        """
        try:
            # Check if token file exists and load credentials
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
                    print("✅ Loaded existing credentials from token file")
            
            # If credentials are invalid or don't exist, authenticate
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    # Refresh expired token
                    print("🔄 Refreshing expired credentials...")
                    self.creds.refresh(Request())
                else:
                    # New authentication flow
                    if not os.path.exists(self.credentials_file):
                        print(f"❌ Credentials file not found: {self.credentials_file}")
                        print("Please download credentials.json from Google Cloud Console")
                        return False
                    
                    print("🔐 Starting OAuth authentication flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for future use
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
                    print("✅ Credentials saved to token file")
            
            # Build the Calendar API service
            self.service = build('calendar', 'v3', credentials=self.creds)
            print("✅ Successfully authenticated with Google Calendar")
            return True
            
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def get_calendar_list(self) -> List[Dict[str, Any]]:
        """
        Retrieve list of all calendars accessible to the user.
        
        Returns:
            list: List of calendar objects
            
        Citation: Calendar List API - https://developers.google.com/calendar/api/v3/reference/calendarList
        """
        try:
            if not self.service:
                print("❌ Service not initialized. Please authenticate first.")
                return []
            
            calendar_list = self.service.calendarList().list().execute()
            calendars = calendar_list.get('items', [])
            
            print(f"✅ Retrieved {len(calendars)} calendars")
            return calendars
            
        except HttpError as error:
            print(f"❌ Error retrieving calendar list: {error}")
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
        Retrieve calendar events within a specified time range.
        
        Args:
            calendar_id (str): Calendar ID (default: 'primary')
            time_min (datetime): Start of time range
            time_max (datetime): End of time range
            max_results (int): Maximum number of events to return
            single_events (bool): Expand recurring events
            order_by (str): Order results by startTime
            
        Returns:
            list: List of event objects
            
        Citation: Events.list API - https://developers.google.com/calendar/api/v3/reference/events/list
        """
        try:
            if not self.service:
                print("❌ Service not initialized. Please authenticate first.")
                return []
            
            # Set default time range if not provided
            if time_min is None:
                time_min = datetime.utcnow()
            if time_max is None:
                time_max = time_min + timedelta(days=7)
            
            # Convert datetime to RFC3339 format
            time_min_str = time_min.isoformat() + 'Z'
            time_max_str = time_max.isoformat() + 'Z'
            
            # Call the Calendar API
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=time_min_str,
                timeMax=time_max_str,
                maxResults=max_results,
                singleEvents=single_events,
                orderBy=order_by
            ).execute()
            
            events = events_result.get('items', [])
            print(f"✅ Retrieved {len(events)} events")
            return events
            
        except HttpError as error:
            print(f"❌ Error retrieving events: {error}")
            return []
    
    def get_today_events(self) -> List[Dict[str, Any]]:
        """
        Get all events for today.
        
        Returns:
            list: List of today's events
        """
        now = datetime.utcnow()
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.get_events(time_min=start_of_day, time_max=end_of_day)
    
    def get_week_events(self) -> List[Dict[str, Any]]:
        """
        Get all events for the current week.
        
        Returns:
            list: List of this week's events
        """
        now = datetime.utcnow()
        end_of_week = now + timedelta(days=7)
        
        return self.get_events(time_min=now, time_max=end_of_week, max_results=50)
    
    def format_event(self, event: Dict[str, Any]) -> str:
        """
        Format a calendar event into a readable string.
        
        Args:
            event (dict): Event object from Google Calendar API
            
        Returns:
            str: Formatted event string
        """
        try:
            summary = event.get('summary', 'No Title')
            start = event.get('start', {})
            end = event.get('end', {})
            location = event.get('location', 'No location')
            description = event.get('description', 'No description')
            
            # Handle all-day events vs timed events
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
                # Truncate long descriptions
                desc = description[:100] + "..." if len(description) > 100 else description
                formatted += f"   📝 {desc}\n"
            
            return formatted
            
        except Exception as e:
            return f"Error formatting event: {e}"
    
    def format_events_list(self, events: List[Dict[str, Any]]) -> str:
        """
        Format a list of events into a readable string.
        
        Args:
            events (list): List of event objects
            
        Returns:
            str: Formatted events list
        """
        if not events:
            return "No upcoming events found."
        
        formatted = f"Found {len(events)} event(s):\n\n"
        for i, event in enumerate(events, 1):
            formatted += f"{i}. {self.format_event(event)}\n"
        
        return formatted
    
    def search_events(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search for events matching a query string.
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            list: List of matching events
        """
        try:
            if not self.service:
                print("❌ Service not initialized. Please authenticate first.")
                return []
            
            now = datetime.utcnow().isoformat() + 'Z'
            
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=max_results,
                q=query,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            print(f"✅ Found {len(events)} events matching '{query}'")
            return events
            
        except HttpError as error:
            print(f"❌ Error searching events: {error}")
            return []


# Example usage and testing
if __name__ == "__main__":
    # Initialize calendar integration
    calendar = CalendarIntegration()
    
    # Test 1: Authentication
    print("\n--- Test 1: Authentication ---")
    if calendar.authenticate():
        print("Authentication successful!")
    else:
        print("Authentication failed!")
        exit(1)
    
    # Test 2: Get calendar list
    print("\n--- Test 2: Calendar List ---")
    calendars = calendar.get_calendar_list()
    for cal in calendars[:3]:  # Show first 3
        print(f"- {cal.get('summary', 'N/A')}")
    
    # Test 3: Get today's events
    print("\n--- Test 3: Today's Events ---")
    today_events = calendar.get_today_events()
    print(calendar.format_events_list(today_events))
    
    # Test 4: Get this week's events
    print("\n--- Test 4: This Week's Events ---")
    week_events = calendar.get_week_events()
    print(f"Total events this week: {len(week_events)}")
    
    # Test 5: Search events
    print("\n--- Test 5: Search Events ---")
    search_results = calendar.search_events("meeting")
    print(calendar.format_events_list(search_results))