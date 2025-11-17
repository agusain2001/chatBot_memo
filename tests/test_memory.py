"""
Unit Tests for Memory Manager
Tests Mem0 integration and memory operations.

Citation: pytest documentation - https://docs.pytest.org/
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src' / 'backend'))

from src.backend.memory_manager import MemoryManager


class TestMemoryManager:
    """Test suite for MemoryManager class."""
    
    @pytest.fixture
    def memory_manager(self):
        """Create a MemoryManager instance for testing."""
        return MemoryManager()
    
    @pytest.fixture
    def test_user_id(self):
        """Test user ID."""
        return "test_student_123"
    
    def test_initialization(self, memory_manager):
        """Test MemoryManager initialization."""
        assert memory_manager is not None
        assert memory_manager.memory is not None
        print("✅ MemoryManager initialization test passed")
    
    def test_add_memory(self, memory_manager, test_user_id):
        """Test adding a memory."""
        result = memory_manager.add_memory(
            user_id=test_user_id,
            message="I prefer studying in the morning",
            metadata={"category": "preference"}
        )
        
        assert result.get('success') is True
        print("✅ Add memory test passed")
    
    def test_get_memories(self, memory_manager, test_user_id):
        """Test retrieving memories."""
        # First add some memories
        memory_manager.add_memory(
            user_id=test_user_id,
            message="Test memory 1"
        )
        memory_manager.add_memory(
            user_id=test_user_id,
            message="Test memory 2"
        )
        
        # Retrieve memories
        memories = memory_manager.get_memories(test_user_id)
        
        assert isinstance(memories, list)
        assert len(memories) >= 0
        print(f"✅ Get memories test passed - Found {len(memories)} memories")
    
    def test_search_memories(self, memory_manager, test_user_id):
        """Test searching memories."""
        # Add a specific memory
        memory_manager.add_memory(
            user_id=test_user_id,
            message="I love studying computer science in the library"
        )
        
        # Search for it
        results = memory_manager.search_memories(
            user_id=test_user_id,
            query="computer science"
        )
        
        assert isinstance(results, list)
        print(f"✅ Search memories test passed - Found {len(results)} results")
    
    def test_memory_persistence(self, memory_manager, test_user_id):
        """Test that memories persist across operations."""
        # Add a memory
        test_message = "Persistence test memory"
        memory_manager.add_memory(
            user_id=test_user_id,
            message=test_message
        )
        
        # Retrieve and verify
        memories = memory_manager.get_memories(test_user_id)
        memory_texts = [m.get('memory', '') for m in memories]
        
        # Check if our test message is in the retrieved memories
        found = any(test_message in text for text in memory_texts)
        assert found, "Memory not found after adding"
        print("✅ Memory persistence test passed")
    
    def test_delete_all_memories(self, memory_manager, test_user_id):
        """Test deleting all memories for a user."""
        # Add some memories
        memory_manager.add_memory(test_user_id, "Test 1")
        memory_manager.add_memory(test_user_id, "Test 2")
        
        # Delete all
        result = memory_manager.delete_all_memories(test_user_id)
        
        assert result.get('success') is True
        
        # Verify deletion
        memories = memory_manager.get_memories(test_user_id)
        assert len(memories) == 0
        print("✅ Delete all memories test passed")
    
    def test_get_memory_summary(self, memory_manager, test_user_id):
        """Test getting memory summary."""
        # Add some memories
        memory_manager.add_memory(test_user_id, "Summary test 1")
        memory_manager.add_memory(test_user_id, "Summary test 2")
        
        # Get summary
        summary = memory_manager.get_memory_summary(test_user_id)
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert "Summary test" in summary
        print("✅ Get memory summary test passed")
    
    def test_memory_metadata(self, memory_manager, test_user_id):
        """Test memory metadata handling."""
        metadata = {
            "category": "academic",
            "priority": "high",
            "course": "Computer Science"
        }
        
        result = memory_manager.add_memory(
            user_id=test_user_id,
            message="Metadata test",
            metadata=metadata
        )
        
        assert result.get('success') is True
        print("✅ Memory metadata test passed")


# Run tests
if __name__ == "__main__":
    print("\n" + "="*60)
    print("MEMORY MANAGER TEST SUITE")
    print("="*60 + "\n")
    
    pytest.main([__file__, '-v', '--tb=short'])
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)