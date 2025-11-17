"""
Streamlit Frontend Application
Interactive web interface for the Student Chatbot with Mem0 and Calendar integration.

Citations:
- Streamlit Documentation: https://docs.streamlit.io/
- Streamlit Session State: https://docs.streamlit.io/library/api-reference/session-state
"""

import streamlit as st
import sys
import os
from datetime import datetime
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent / 'backend'))

from backend.chatbot import StudentChatbot
from backend.memory_manager import MemoryManager
from backend.calendar_integration import CalendarIntegration


# Page configuration
# Citation: Streamlit page config - https://docs.streamlit.io/library/api-reference/utilities/st.set_page_config
st.set_page_config(
    page_title="Student Schedule Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f5f5f5;
        border-left: 4px solid #4caf50;
    }
    .sidebar-info {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    
    if 'memory_manager' not in st.session_state:
        st.session_state.memory_manager = None
    
    if 'calendar' not in st.session_state:
        st.session_state.calendar = None
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "default_user"
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    
    if 'calendar_authenticated' not in st.session_state:
        st.session_state.calendar_authenticated = False


def initialize_components():
    """Initialize chatbot components."""
    try:
        with st.spinner("Initializing chatbot components..."):
            # Initialize Memory Manager
            st.session_state.memory_manager = MemoryManager()
            
            # Initialize Calendar Integration
            st.session_state.calendar = CalendarIntegration()
            
            # Initialize Chatbot
            st.session_state.chatbot = StudentChatbot(
                memory_manager=st.session_state.memory_manager,
                calendar_integration=st.session_state.calendar
            )
            
            st.session_state.initialized = True
            st.success("✅ Chatbot initialized successfully!")
            
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.session_state.initialized = False


def authenticate_calendar():
    """Handle calendar authentication."""
    try:
        with st.spinner("Authenticating with Google Calendar..."):
            success = st.session_state.calendar.authenticate()
            if success:
                st.session_state.calendar_authenticated = True
                st.success("✅ Calendar authenticated successfully!")
                return True
            else:
                st.error("❌ Calendar authentication failed. Please check credentials.")
                return False
    except Exception as e:
        st.error(f"❌ Authentication error: {e}")
        return False


def display_chat_message(role: str, content: str, timestamp: str = None):
    """
    Display a chat message with styling.
    
    Args:
        role (str): 'user' or 'assistant'
        content (str): Message content
        timestamp (str): Message timestamp
    """
    css_class = "user-message" if role == "user" else "assistant-message"
    icon = "👤" if role == "user" else "🤖"
    
    timestamp_str = ""
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp)
            timestamp_str = f"<small>{dt.strftime('%I:%M %p')}</small>"
        except:
            pass
    
    st.markdown(f"""
        <div class="chat-message {css_class}">
            <strong>{icon} {role.capitalize()}</strong> {timestamp_str}
            <p>{content}</p>
        </div>
    """, unsafe_allow_html=True)


def main():
    """Main application function."""
    
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🎓 Student Schedule Assistant</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # User ID input
        user_id = st.text_input(
            "User ID",
            value=st.session_state.user_id,
            help="Enter your unique student ID"
        )
        if user_id != st.session_state.user_id:
            st.session_state.user_id = user_id
            st.session_state.chat_history = []
        
        st.markdown("---")
        
        # Initialize button
        if not st.session_state.initialized:
            if st.button("🚀 Initialize Chatbot", use_container_width=True):
                initialize_components()
        else:
            st.success("✅ Chatbot Ready")
        
        st.markdown("---")
        
        # Calendar authentication
        st.header("📅 Calendar Access")
        if not st.session_state.calendar_authenticated:
            st.info("Calendar not connected. Authenticate to access your schedule.")
            if st.button("🔐 Authenticate Calendar", use_container_width=True):
                authenticate_calendar()
        else:
            st.success("✅ Calendar Connected")
            if st.button("🔄 Re-authenticate", use_container_width=True):
                authenticate_calendar()
        
        st.markdown("---")
        
        # Memory management
        st.header("🧠 Memory")
        if st.session_state.initialized and st.session_state.memory_manager:
            if st.button("📚 View Memories", use_container_width=True):
                memories = st.session_state.memory_manager.get_memories(
                    st.session_state.user_id,
                    limit=10
                )
                if memories:
                    st.subheader("Stored Memories")
                    for i, mem in enumerate(memories, 1):
                        st.text(f"{i}. {mem.get('memory', 'N/A')}")
                else:
                    st.info("No memories stored yet.")
            
            if st.button("🗑️ Clear Memories", use_container_width=True):
                result = st.session_state.memory_manager.delete_all_memories(
                    st.session_state.user_id
                )
                if result.get('success'):
                    st.success("Memories cleared!")
                else:
                    st.error("Failed to clear memories.")
        
        st.markdown("---")
        
        # Clear chat
        if st.button("🔄 Clear Chat History", use_container_width=True):
            st.session_state.chat_history = []
            if st.session_state.chatbot:
                st.session_state.chatbot.reset_conversation(st.session_state.user_id)
            st.rerun()
        
        st.markdown("---")
        
        # Statistics
        if st.session_state.initialized and st.session_state.chatbot:
            st.header("📊 Statistics")
            stats = st.session_state.chatbot.get_statistics(st.session_state.user_id)
            st.metric("Total Messages", stats.get('total_messages', 0))
            st.metric("Stored Memories", stats.get('stored_memories', 0))
        
        st.markdown("---")
        
        # Help section
        with st.expander("ℹ️ How to Use"):
            st.markdown("""
            **Features:**
            1. **Memory Management**: Tell the chatbot your preferences
            2. **Calendar Access**: View your schedule and meetings
            3. **Smart Conversations**: Get personalized recommendations
            
            **Example Queries:**
            - "I prefer studying in the morning"
            - "Show my meetings for today"
            - "What are my study preferences?"
            - "What's my schedule this week?"
            """)
    
    # Main chat interface
    if not st.session_state.initialized:
        st.info("👈 Please initialize the chatbot using the sidebar.")
        
        # Quick start guide
        st.subheader("🚀 Quick Start Guide")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            #### 1️⃣ Initialize
            Click the **Initialize Chatbot** button in the sidebar.
            """)
        
        with col2:
            st.markdown("""
            #### 2️⃣ Authenticate
            Connect your Google Calendar for schedule access.
            """)
        
        with col3:
            st.markdown("""
            #### 3️⃣ Chat
            Start chatting with your AI assistant!
            """)
        
        return
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            display_chat_message(
                message['role'],
                message['content'],
                message.get('timestamp')
            )
    
    # Chat input
    st.markdown("---")
    
    # Sample queries for quick access
    st.subheader("💡 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📅 Today's Schedule"):
            user_input = "What are my meetings today?"
    with col2:
        if st.button("📆 This Week"):
            user_input = "Show me my schedule for this week"
    with col3:
        if st.button("🧠 My Memories"):
            user_input = "What do you know about my preferences?"
    with col4:
        if st.button("⏰ Study Times"):
            user_input = "When do I prefer to study?"
    
    # Main chat input
    user_input = st.chat_input("Type your message here...", key="chat_input")
    
    if user_input:
        # Add user message to history
        st.session_state.chat_history.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        
        # Get bot response
        with st.spinner("Thinking..."):
            try:
                response = st.session_state.chatbot.chat(
                    st.session_state.user_id,
                    user_input
                )
                
                # Add bot response to history
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
                
            except Exception as e:
                st.error(f"Error generating response: {e}")
                response = "I encountered an error processing your request. Please try again."
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': datetime.now().isoformat()
                })
        
        # Rerun to update chat display
        st.rerun()


if __name__ == "__main__":
    main()