"""
Unit Tests for Chatbot
Tests main chatbot functionality and integration.

Citation: pytest documentation - https://docs.pytest.org/
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src' / 'backend'))

from src.backend.chatbot import StudentChatbot
from src.backend.memory_manager import MemoryManager
from src.backend.calendar_integration import CalendarIntegration


class TestStudentChatbot:
    """Test suite for StudentChatbot class."""
    
    @pytest.fixture
    def chatbot(self):
        """Create a chatbot instance for testing."""
        return StudentChatbot()
    
    @pytest.fixture
    def test_user_id(self):
        """Test user ID."""
        return "test_user_456"
    
    def test_initialization(self, chatbot):
        """Test chatbot initialization."""
        assert chatbot is not None
        assert chatbot.memory_manager is not None
        assert chatbot.calendar is not None
        assert chatbot.system_prompt is not None
        print("✅ Chatbot initialization test passed")
    
    def test_detect_intent_calendar(self, chatbot):
        """Test intent detection for calendar queries."""
        test_messages = [
            "What are my meetings today?",
            "Show me my schedule",
            "When is my next appointment?"
        ]
        
        for msg in test_messages:
            intent = chatbot._detect_intent(msg)
            assert intent == 'calendar_query'
        
        print("✅ Calendar intent detection test passed")
    
    def test_detect_intent_memory_storage(self, chatbot):
        """Test intent detection for memory storage."""
        test_messages = [
            "Remember that I prefer morning study",
            "I like to take breaks every hour",
            "Note that my favorite subject is CS"
        ]
        
        for msg in test_messages:
            intent = chatbot._detect_intent(msg)
            assert intent == 'store_memory'
        
        print("✅ Memory storage intent detection test passed")
    
    def test_detect_intent_memory_recall(self, chatbot):
        """Test intent detection for memory recall."""
        test_messages = [
            "What do you know about me?",
            "What are my preferences?",
            "Remind me of my study habits"
        ]
        
        for msg in test_messages:
            intent = chatbot._detect_intent(msg)
            assert intent == 'recall_memory'
        
        print("✅ Memory recall intent detection test passed")
    
    def test_conversation_history(self, chatbot, test_user_id):
        """Test conversation history management."""
        # Add messages
        chatbot._add_to_history(test_user_id, "user", "Hello")
        chatbot._add_to_history(test_user_id, "assistant", "Hi there!")
        
        # Get history
        history = chatbot._get_conversation_history(test_user_id)
        
        assert len(history) == 2
        assert history[0]['role'] == 'user'
        assert history[1]['role'] == 'assistant'
        print("✅ Conversation history test passed")
    
    def test_handle_memory_storage(self, chatbot, test_user_id):
        """Test memory storage handler."""
        message = "Remember that I prefer studying in the library"
        
        response = chatbot._handle_memory_storage(test_user_id, message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        assert "note" in response.lower() or "remember" in response.lower()
        print("✅ Memory storage handler test passed")
    
    def test_handle_memory_recall(self, chatbot, test_user_id):
        """Test memory recall handler."""
        # First add some memories
        chatbot._handle_memory_storage(test_user_id, "I like morning study")
        chatbot._handle_memory_storage(test_user_id, "My favorite subject is CS")
        
        # Recall memories
        response = chatbot._handle_memory_recall(test_user_id, "What do you know?")
        
        assert isinstance(response, str)
        assert len(response) > 0
        print("✅ Memory recall handler test passed")
    
    def test_chat_method(self, chatbot, test_user_id):
        """Test main chat method."""
        test_message = "Hello, I prefer morning study sessions"
        
        response = chatbot.chat(test_user_id, test_message)
        
        assert isinstance(response, str)
        assert len(response) > 0
        
        # Check that it was added to history
        history = chatbot._get_conversation_history(test_user_id)
        assert len(history) >= 2  # User message + assistant response
        print("✅ Chat method test passed")
    
    def test_reset_conversation(self, chatbot, test_user_id):
        """Test conversation reset."""
        # Add some messages
        chatbot.chat(test_user_id, "Test message 1")
        chatbot.chat(test_user_id, "Test message 2")
        
        # Reset
        chatbot.reset_conversation(test_user_id)
        
        # Check history is empty
        history = chatbot._get_conversation_history(test_user_id)
        assert len(history) == 0
        print("✅ Conversation reset test passed")
    
    def test_get_statistics(self, chatbot, test_user_id):
        """Test statistics retrieval."""
        # Add some interactions
        chatbot.chat(test_user_id, "Test 1")
        chatbot.chat(test_user_id, "Remember I like mornings")
        
        # Get statistics
        stats = chatbot.get_statistics(test_user_id)
        
        assert isinstance(stats, dict)
        assert 'total_messages' in stats
        assert 'stored_memories' in stats
        assert stats['total_messages'] >= 2
        print("✅ Statistics retrieval test passed")
    
    def test_multiple_users(self, chatbot):
        """Test handling multiple users."""
        user1 = "user_001"
        user2 = "user_002"
        
        # Different messages for different users
        chatbot.chat(user1, "I prefer morning study")
        chatbot.chat(user2, "I prefer evening study")
        
        # Get histories
        history1 = chatbot._get_conversation_history(user1)
        history2 = chatbot._get_conversation_history(user2)
        
        # Ensure they're separate
        assert len(history1) > 0
        assert len(history2) > 0
        assert history1 != history2
        print("✅ Multiple users test passed")


# Integration Tests
class TestChatbotIntegration:
    """Integration tests for complete chatbot workflow."""
    
    @pytest.fixture
    def chatbot(self):
        """Create a chatbot instance."""
        return StudentChatbot()
    
    @pytest.fixture
    def test_user_id(self):
        """Test user ID."""
        return "integration_test_user"
    
    def test_memory_and_chat_integration(self, chatbot, test_user_id):
        """Test integration between memory and chat."""
        # Store a preference
        response1 = chatbot.chat(
            test_user_id,
            "Remember that I study best in the morning"
        )
        assert len(response1) > 0
        
        # Ask about preferences
        response2 = chatbot.chat(
            test_user_id,
            "What do you know about my study preferences?"
        )
        assert len(response2) > 0
        assert "morning" in response2.lower()
        print("✅ Memory and chat integration test passed")
    
    def test_conversation_flow(self, chatbot, test_user_id):
        """Test natural conversation flow."""
        messages = [
            "Hi, I'm a new student",
            "I prefer studying in the morning",
            "What do you remember about me?",
            "Thanks for remembering!"
        ]
        
        for msg in messages:
            response = chatbot.chat(test_user_id, msg)
            assert isinstance(response, str)
            assert len(response) > 0
        
        # Check conversation history
        history = chatbot._get_conversation_history(test_user_id)
        assert len(history) == len(messages) * 2  # User + assistant for each
        print("✅ Conversation flow test passed")


# Run tests
if __name__ == "__main__":
    print("\n" + "="*60)
    print("CHATBOT TEST SUITE")
    print("="*60 + "\n")
    
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)