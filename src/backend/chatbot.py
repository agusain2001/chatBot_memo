"""
Main Chatbot Module
Integrates Mem0 memory management and MCP calendar functionality with conversational AI.

Citations:
- OpenAI API: https://platform.openai.com/docs/api-reference
- LangChain: https://python.langchain.com/docs/get_started/introduction
- Mem0 Library: https://docs.mem0.ai/
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import re

from memory_manager import MemoryManager
from calendar_integration import CalendarIntegration

try:
    from openai import OpenAI
except ImportError:
    print("OpenAI library not installed. Install with: pip install openai")
    OpenAI = None


class StudentChatbot:
    """
    Intelligent chatbot that combines memory management and calendar integration
    to assist students with scheduling and personalized interactions.
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        memory_manager: Optional[MemoryManager] = None,
        calendar_integration: Optional[CalendarIntegration] = None
    ):
        """
        Initialize the Student Chatbot.
        
        Args:
            openai_api_key (str, optional): OpenAI API key
            memory_manager (MemoryManager, optional): Memory manager instance
            calendar_integration (CalendarIntegration, optional): Calendar integration instance
        """
        # Initialize OpenAI client
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if OpenAI and self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)
        else:
            self.client = None
            print("⚠️  OpenAI client not initialized")
        
        # Initialize components
        self.memory_manager = memory_manager or MemoryManager()
        self.calendar = calendar_integration or CalendarIntegration()
        
        # Conversation history
        self.conversation_history: Dict[str, List[Dict]] = {}
        
        # System prompt for the chatbot
        self.system_prompt = """You are a helpful AI assistant for students. Your capabilities include:
1. Remembering student preferences, study habits, and personal information
2. Accessing and displaying calendar schedules and meetings
3. Providing personalized recommendations based on stored memories
4. Helping with time management and scheduling

Always be friendly, supportive, and focused on helping students succeed.
When discussing schedules, be clear about dates and times.
When you learn new information about a student, acknowledge that you'll remember it."""
        
        print("🤖 Student Chatbot initialized successfully")
    
    def _get_conversation_history(self, user_id: str) -> List[Dict]:
        """Get conversation history for a user."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        return self.conversation_history[user_id]
    
    def _add_to_history(self, user_id: str, role: str, content: str):
        """Add a message to conversation history."""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        self.conversation_history[user_id].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def _detect_intent(self, message: str) -> str:
        """
        Detect the user's intent from their message.
        
        Args:
            message (str): User message
            
        Returns:
            str: Detected intent
        """
        message_lower = message.lower()
        
        # Calendar-related intents
        calendar_keywords = [
            'schedule', 'meeting', 'calendar', 'event', 'appointment',
            'today', 'tomorrow', 'this week', 'next week', 'when is'
        ]
        if any(keyword in message_lower for keyword in calendar_keywords):
            return 'calendar_query'
        
        # Memory storage intents
        memory_keywords = [
            'remember', 'i prefer', 'my favorite', 'i like', 'i usually',
            'note that', 'keep in mind'
        ]
        if any(keyword in message_lower for keyword in memory_keywords):
            return 'store_memory'
        
        # Memory retrieval intents
        recall_keywords = [
            'what do you know about me', 'what have i told you',
            'my preferences', 'what do i like', 'remind me'
        ]
        if any(keyword in message_lower for keyword in recall_keywords):
            return 'recall_memory'
        
        return 'general_conversation'
    
    def _handle_calendar_query(self, user_id: str, message: str) -> str:
        """
        Handle calendar-related queries.
        
        Args:
            user_id (str): User ID
            message (str): User message
            
        Returns:
            str: Response with calendar information
        """
        try:
            message_lower = message.lower()
            
            # Authenticate if not already done
            if not self.calendar.service:
                auth_success = self.calendar.authenticate()
                if not auth_success:
                    return "I'm having trouble accessing your calendar. Please ensure you've granted permission and try again."
            
            # Determine time range based on query
            if 'today' in message_lower:
                events = self.calendar.get_today_events()
                time_frame = "today"
            elif 'this week' in message_lower or 'week' in message_lower:
                events = self.calendar.get_week_events()
                time_frame = "this week"
            elif 'tomorrow' in message_lower:
                tomorrow = datetime.utcnow() + timedelta(days=1)
                tomorrow_start = tomorrow.replace(hour=0, minute=0, second=0)
                tomorrow_end = tomorrow_start + timedelta(days=1)
                events = self.calendar.get_events(time_min=tomorrow_start, time_max=tomorrow_end)
                time_frame = "tomorrow"
            else:
                # Default to next 7 days
                events = self.calendar.get_week_events()
                time_frame = "upcoming"
            
            if not events:
                return f"You don't have any events scheduled for {time_frame}. Your schedule is clear!"
            
            # Format the response
            response = f"Here are your events for {time_frame}:\n\n"
            response += self.calendar.format_events_list(events)
            
            # Check memories for relevant preferences
            memories = self.memory_manager.search_memories(user_id, "study schedule preference")
            if memories:
                response += f"\n💡 Based on your preferences: {memories[0].get('memory', '')}"
            
            return response
            
        except Exception as e:
            return f"I encountered an error while accessing your calendar: {str(e)}"
    
    def _handle_memory_storage(self, user_id: str, message: str) -> str:
        """
        Store information from the user message into memory.
        
        Args:
            user_id (str): User ID
            message (str): User message
            
        Returns:
            str: Confirmation message
        """
        try:
            # Store the memory
            result = self.memory_manager.add_memory(
                user_id=user_id,
                message=message,
                metadata={"category": "user_preference", "source": "conversation"}
            )
            
            if result.get('success'):
                return "Got it! I've made a note of that and will remember it for future conversations. 📝"
            else:
                return "I tried to remember that, but encountered an issue. Could you try rephrasing?"
                
        except Exception as e:
            return f"I had trouble storing that information: {str(e)}"
    
    def _handle_memory_recall(self, user_id: str, message: str) -> str:
        """
        Recall and present stored memories.
        
        Args:
            user_id (str): User ID
            message (str): User message
            
        Returns:
            str: Memory information
        """
        try:
            memories = self.memory_manager.get_memories(user_id, limit=10)
            
            if not memories:
                return "I don't have any stored information about you yet. Feel free to share your preferences, and I'll remember them!"
            
            response = "Here's what I remember about you:\n\n"
            for i, mem in enumerate(memories, 1):
                memory_text = mem.get('memory', 'N/A')
                response += f"{i}. {memory_text}\n"
            
            response += "\nIs there anything else you'd like me to know?"
            return response
            
        except Exception as e:
            return f"I had trouble retrieving your information: {str(e)}"
    
    def _generate_ai_response(self, user_id: str, message: str, context: str = "") -> str:
        """
        Generate a response using OpenAI's API with context.
        
        Args:
            user_id (str): User ID
            message (str): User message
            context (str): Additional context
            
        Returns:
            str: AI-generated response
        """
        if not self.client:
            return "I'm currently unable to generate responses. Please check the OpenAI API configuration."
        
        try:
            # Get relevant memories for context
            memories = self.memory_manager.search_memories(user_id, message, limit=3)
            memory_context = ""
            if memories:
                memory_context = "\n\nRelevant information about the user:\n"
                for mem in memories:
                    memory_context += f"- {mem.get('memory', '')}\n"
            
            # Build messages for the API
            messages = [
                {"role": "system", "content": self.system_prompt + memory_context}
            ]
            
            # Add recent conversation history
            history = self._get_conversation_history(user_id)[-5:]  # Last 5 messages
            for msg in history:
                if msg['role'] in ['user', 'assistant']:
                    messages.append({
                        "role": msg['role'],
                        "content": msg['content']
                    })
            
            # Add current message with any additional context
            current_content = message
            if context:
                current_content += f"\n\nAdditional context: {context}"
            
            messages.append({"role": "user", "content": current_content})
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I encountered an error generating a response: {str(e)}"
    
    def chat(self, user_id: str, message: str) -> str:
        """
        Main chat method that processes user input and generates responses.
        
        Args:
            user_id (str): Unique user identifier
            message (str): User's message
            
        Returns:
            str: Chatbot's response
        """
        # Add user message to history
        self._add_to_history(user_id, "user", message)
        
        # Detect intent
        intent = self._detect_intent(message)
        
        # Route to appropriate handler
        if intent == 'calendar_query':
            response = self._handle_calendar_query(user_id, message)
        elif intent == 'store_memory':
            # Store the memory
            memory_response = self._handle_memory_storage(user_id, message)
            # Also generate a conversational response
            ai_response = self._generate_ai_response(user_id, message)
            response = memory_response + "\n\n" + ai_response
        elif intent == 'recall_memory':
            response = self._handle_memory_recall(user_id, message)
        else:
            # General conversation
            response = self._generate_ai_response(user_id, message)
        
        # Add assistant response to history
        self._add_to_history(user_id, "assistant", response)
        
        return response
    
    def reset_conversation(self, user_id: str):
        """Reset conversation history for a user."""
        if user_id in self.conversation_history:
            self.conversation_history[user_id] = []
            print(f"✅ Conversation reset for user {user_id}")
    
    def get_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Get statistics about the user's interactions.
        
        Args:
            user_id (str): User ID
            
        Returns:
            dict: Statistics dictionary
        """
        history = self._get_conversation_history(user_id)
        memories = self.memory_manager.get_memories(user_id)
        
        return {
            "total_messages": len(history),
            "stored_memories": len(memories),
            "conversation_started": history[0]['timestamp'] if history else None,
            "last_interaction": history[-1]['timestamp'] if history else None
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize chatbot
    chatbot = StudentChatbot()
    
    # Test user
    test_user = "student_001"
    
    print("\n" + "="*60)
    print("STUDENT CHATBOT - INTERACTIVE TEST")
    print("="*60)
    
    # Test conversations
    test_queries = [
        "Hi! I prefer studying in the morning between 7-9 AM.",
        "What are my meetings for today?",
        "Remember that I like to take breaks every 45 minutes.",
        "What do you know about my study preferences?",
        "Show me my schedule for this week."
    ]
    
    for query in test_queries:
        print(f"\n👤 User: {query}")
        response = chatbot.chat(test_user, query)
        print(f"🤖 Assistant: {response}")
        print("-" * 60)
    
    # Show statistics
    print("\n📊 Session Statistics:")
    stats = chatbot.get_statistics(test_user)
    for key, value in stats.items():
        print(f"  {key}: {value}")