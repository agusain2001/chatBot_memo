"""
Memory Manager Module
Handles all memory operations using the Mem0 library for persistent student data storage.

Citation: 
- Mem0 Library Documentation: https://docs.mem0.ai/
- Mem0 GitHub: https://github.com/mem0ai/mem0
"""

import os
from typing import List, Dict, Optional, Any
from datetime import datetime
import json
from mem0 import Memory

class MemoryManager:
    """
    Manages student memories using Mem0 library.
    Handles creation, retrieval, updating, and deletion of memories.
    """
    
    def __init__(self, api_key: Optional[str] = None, config: Optional[Dict] = None):
        """
        Initialize the Memory Manager with Mem0 configuration.
        
        Args:
            api_key (str, optional): Mem0 API key
            config (dict, optional): Custom Mem0 configuration
            
        Citation: Mem0 initialization - https://docs.mem0.ai/quickstart
        """
        self.api_key = api_key or os.getenv('MEM0_API_KEY')
        
        # Default configuration for Mem0
        # Citation: Mem0 configuration options - https://docs.mem0.ai/configuration
        self.config = config or {
            "vector_store": {
                "provider": "qdrant",
                "config": {
                    "collection_name": "student_memories",
                    "embedding_model_dims": 1536,
                }
            },
            "llm": {
                "provider": "openai",
                "config": {
                    "model": "gpt-4",
                    "temperature": 0.2,
                    "max_tokens": 1500,
                }
            },
            "embedder": {
                "provider": "openai",
                "config": {
                    "model": "text-embedding-ada-002"
                }
            }
        }
        
        # Initialize Mem0 Memory instance
        try:
            self.memory = Memory.from_config(self.config)
            print("✅ Memory Manager initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing Memory Manager: {e}")
            self.memory = None
    
    def add_memory(self, user_id: str, message: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Add a new memory for a user.
        
        Args:
            user_id (str): Unique identifier for the user
            message (str): Memory content to store
            metadata (dict, optional): Additional metadata
            
        Returns:
            dict: Result of the memory addition operation
            
        Citation: Mem0 add operation - https://docs.mem0.ai/api-reference/add
        """
        try:
            if not self.memory:
                return {"error": "Memory system not initialized"}
            
            # Add timestamp to metadata
            if metadata is None:
                metadata = {}
            metadata['timestamp'] = datetime.now().isoformat()
            
            # Add memory using Mem0
            result = self.memory.add(
                messages=message,
                user_id=user_id,
                metadata=metadata
            )
            
            print(f"✅ Memory added for user {user_id}: {message[:50]}...")
            return {
                "success": True,
                "result": result,
                "message": "Memory stored successfully"
            }
            
        except Exception as e:
            print(f"❌ Error adding memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_memories(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve all memories for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            limit (int): Maximum number of memories to retrieve
            
        Returns:
            list: List of memory objects
            
        Citation: Mem0 get_all operation - https://docs.mem0.ai/api-reference/get-all
        """
        try:
            if not self.memory:
                return []
            
            # Retrieve memories for the user
            memories = self.memory.get_all(user_id=user_id, limit=limit)
            
            print(f"✅ Retrieved {len(memories)} memories for user {user_id}")
            return memories
            
        except Exception as e:
            print(f"❌ Error retrieving memories: {e}")
            return []
    
    def search_memories(self, user_id: str, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for specific memories using semantic search.
        
        Args:
            user_id (str): Unique identifier for the user
            query (str): Search query
            limit (int): Maximum number of results
            
        Returns:
            list: List of relevant memories
            
        Citation: Mem0 search operation - https://docs.mem0.ai/api-reference/search
        """
        try:
            if not self.memory:
                return []
            
            # Search memories using semantic similarity
            results = self.memory.search(
                query=query,
                user_id=user_id,
                limit=limit
            )
            
            print(f"✅ Found {len(results)} memories matching query: {query[:30]}...")
            return results
            
        except Exception as e:
            print(f"❌ Error searching memories: {e}")
            return []
    
    def update_memory(self, memory_id: str, data: str) -> Dict[str, Any]:
        """
        Update an existing memory.
        
        Args:
            memory_id (str): ID of the memory to update
            data (str): New memory content
            
        Returns:
            dict: Result of the update operation
            
        Citation: Mem0 update operation - https://docs.mem0.ai/api-reference/update
        """
        try:
            if not self.memory:
                return {"error": "Memory system not initialized"}
            
            # Update the memory
            result = self.memory.update(
                memory_id=memory_id,
                data=data
            )
            
            print(f"✅ Memory {memory_id} updated successfully")
            return {
                "success": True,
                "result": result
            }
            
        except Exception as e:
            print(f"❌ Error updating memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_memory(self, memory_id: str) -> Dict[str, Any]:
        """
        Delete a specific memory.
        
        Args:
            memory_id (str): ID of the memory to delete
            
        Returns:
            dict: Result of the deletion operation
            
        Citation: Mem0 delete operation - https://docs.mem0.ai/api-reference/delete
        """
        try:
            if not self.memory:
                return {"error": "Memory system not initialized"}
            
            # Delete the memory
            self.memory.delete(memory_id=memory_id)
            
            print(f"✅ Memory {memory_id} deleted successfully")
            return {
                "success": True,
                "message": "Memory deleted successfully"
            }
            
        except Exception as e:
            print(f"❌ Error deleting memory: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_all_memories(self, user_id: str) -> Dict[str, Any]:
        """
        Delete all memories for a specific user.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            dict: Result of the deletion operation
        """
        try:
            if not self.memory:
                return {"error": "Memory system not initialized"}
            
            # Delete all memories for the user
            self.memory.delete_all(user_id=user_id)
            
            print(f"✅ All memories deleted for user {user_id}")
            return {
                "success": True,
                "message": f"All memories deleted for user {user_id}"
            }
            
        except Exception as e:
            print(f"❌ Error deleting all memories: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_memory_summary(self, user_id: str) -> str:
        """
        Get a formatted summary of all user memories.
        
        Args:
            user_id (str): Unique identifier for the user
            
        Returns:
            str: Formatted memory summary
        """
        try:
            memories = self.get_memories(user_id)
            
            if not memories:
                return "No memories found for this user."
            
            summary = f"📚 Memory Summary for User {user_id}\n"
            summary += "=" * 50 + "\n\n"
            
            for i, mem in enumerate(memories, 1):
                summary += f"{i}. {mem.get('memory', 'N/A')}\n"
                if 'metadata' in mem:
                    summary += f"   Timestamp: {mem['metadata'].get('timestamp', 'N/A')}\n"
                summary += "\n"
            
            return summary
            
        except Exception as e:
            return f"Error generating summary: {e}"


# Example usage and testing
if __name__ == "__main__":
    # Initialize the memory manager
    manager = MemoryManager()
    
    # Test user ID
    test_user = "student_123"
    
    # Test 1: Add memories
    print("\n--- Test 1: Adding Memories ---")
    manager.add_memory(
        user_id=test_user,
        message="I prefer studying in the morning between 7-9 AM",
        metadata={"category": "preference"}
    )
    
    manager.add_memory(
        user_id=test_user,
        message="I have a Computer Science exam on Friday",
        metadata={"category": "academic"}
    )
    
    # Test 2: Retrieve memories
    print("\n--- Test 2: Retrieving Memories ---")
    memories = manager.get_memories(test_user)
    for mem in memories:
        print(f"- {mem.get('memory', 'N/A')}")
    
    # Test 3: Search memories
    print("\n--- Test 3: Searching Memories ---")
    results = manager.search_memories(test_user, "study time")
    for result in results:
        print(f"- {result.get('memory', 'N/A')}")
    
    # Test 4: Get summary
    print("\n--- Test 4: Memory Summary ---")
    print(manager.get_memory_summary(test_user))