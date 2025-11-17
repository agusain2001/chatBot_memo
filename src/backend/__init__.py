"""
Backend Module Initialization
Provides easy imports for the chatbot backend components.

Author: [Your Name]
Date: November 2024
Assignment: AI Internship - Chatbot with Mem0 and MCP Integration
"""

from .memory_manager import MemoryManager
from .calendar_integration import CalendarIntegration
from .chatbot import StudentChatbot

__all__ = [
    'MemoryManager',
    'CalendarIntegration',
    'StudentChatbot'
]

__version__ = '1.0.0'
__author__ = 'Your Name'

# Module information
__doc__ = """
Student Schedule Assistant Backend

This module provides the core functionality for the chatbot including:
- Memory management using Mem0
- Calendar integration using MCP and Google Calendar API
- Intelligent chatbot with context awareness

Citations:
- Mem0: https://docs.mem0.ai/
- MCP SDK: https://github.com/modelcontextprotocol/python-sdk
- Google Calendar API: https://developers.google.com/calendar/api
"""