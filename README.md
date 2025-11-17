# Student Schedule Assistant Chatbot
**AI Internship Assignment - Complete Implementation**

A sophisticated chatbot that combines memory management using Mem0 library and calendar integration through MCP for personalized student assistance.

---

## 🎯 Features

### ✅ Task 1: Mem0 Memory Management
- Persistent memory storage for student preferences and information
- Add, update, retrieve, and delete memories
- Semantic search across stored memories
- Session persistence across conversations

### ✅ Task 2: MCP Calendar Integration
- Google Calendar authentication using OAuth 2.0
- Fetch and display calendar events
- Support for today, week, and custom date range queries
- Secure token handling and data privacy

### ✅ Task 3: Streamlit Frontend
- Interactive web-based user interface
- Real-time chat functionality
- Memory and calendar management controls
- Statistics and conversation history

### 🌟 Bonus Features
- Natural Language Processing for complex queries
- Personalized recommendations based on stored preferences
- Advanced time management suggestions
- Comprehensive error handling and logging

---

## 📁 Project Structure

```
chatbot-mem0-mcp/
├── README.md                          # Project documentation
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
├── run.sh                             # Quick start script
│
├── src/
│   ├── backend/
│   │   ├── chatbot.py                # Main chatbot logic
│   │   ├── memory_manager.py         # Mem0 memory operations
│   │   ├── calendar_integration.py   # MCP calendar integration
│   │   ├── auth_handler.py           # Authentication logic
│   │   └── __init__.py
│   │
│   ├── frontend/
│   │   ├── app.py                    # Streamlit application
│   │   └── ui_components.py          # Reusable UI components
│   │
│   ├── config/
│   │   ├── settings.py               # Configuration settings
│   │   └── mcp_config.json           # MCP configuration
│   │
│   └── utils/
│       ├── helpers.py                # Helper functions
│       └── nlp_processor.py          # NLP processing (bonus)
│
├── tests/
│   ├── test_memory.py                # Memory tests
│   ├── test_calendar.py              # Calendar integration tests
│   └── test_chatbot.py               # Chatbot functionality tests
│
├── docs/
│   ├── Sample_Responses.txt          # Test queries and responses
│   ├── SETUP.md                      # Detailed setup instructions
│   └── API_DOCUMENTATION.md          # API documentation
│
├── data/                              # Data storage directory
└── logs/                              # Application logs
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Google Cloud Platform account
- OpenAI API key
- Mem0 API key

### Installation

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd chatbot-mem0-mcp
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys and credentials
```

4. **Set up Google Calendar API:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project
   - Enable Google Calendar API
   - Create OAuth 2.0 credentials
   - Download `credentials.json` to project root

5. **Run the application:**
```bash
streamlit run src/frontend/app.py
```

Or use the quick start script:
```bash
chmod +x run.sh
./run.sh
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Mem0 Configuration
MEM0_API_KEY=your_mem0_api_key_here

# Google Calendar
GOOGLE_CLIENT_ID=your_client_id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8501

# Application Settings
APP_NAME=Student Schedule Assistant
DEBUG_MODE=True
```

### Google Calendar Setup

1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google Calendar API
4. Create OAuth 2.0 Client ID credentials
5. Download credentials as `credentials.json`
6. Place in project root directory

---

## 📖 Usage Guide

### Starting the Application

1. **Launch Streamlit:**
```bash
streamlit run src/frontend/app.py
```

2. **Initialize the chatbot** using the sidebar button

3. **Authenticate calendar access** when prompted

4. **Start chatting!**

### Example Interactions

#### Memory Storage:
```
User: "Remember that I prefer studying in the morning between 7-9 AM."
Bot: "Got it! I've made a note of that and will remember it for future conversations. 📝"
```

#### Calendar Queries:
```
User: "What are my meetings today?"
Bot: "Here are your events for today:

1. 📅 **Team Meeting**
   ⏰ 10:00 AM - 11:00 AM
   📍 Conference Room A

2. 📅 **Study Session**
   ⏰ 02:00 PM - 04:00 PM
   📝 Prepare for CS exam"
```

#### Memory Recall:
```
User: "What do you know about my study preferences?"
Bot: "Here's what I remember about you:

1. I prefer studying in the morning between 7-9 AM.
2. I like to take breaks every 45 minutes.
3. My favorite study location is the library."
```

---

## 🧪 Testing

### Run Unit Tests
```bash
# Test memory manager
python tests/test_memory.py

# Test calendar integration
python tests/test_calendar.py

# Test chatbot
python tests/test_chatbot.py

# Run all tests
pytest tests/
```

### Manual Testing
```bash
# Test memory manager
python src/backend/memory_manager.py

# Test calendar integration
python src/backend/calendar_integration.py

# Test chatbot
python src/backend/chatbot.py
```

---

## 📚 Documentation

### Citations and References

#### Mem0 Library
- **Documentation:** https://docs.mem0.ai/
- **GitHub:** https://github.com/mem0ai/mem0
- **API Reference:** https://docs.mem0.ai/api-reference

#### MCP (Model Context Protocol)
- **Python SDK:** https://github.com/modelcontextprotocol/python-sdk
- **Documentation:** https://modelcontextprotocol.io/

#### Google Calendar API
- **Quick Start:** https://developers.google.com/calendar/api/quickstart/python
- **API Reference:** https://developers.google.com/calendar/api/v3/reference
- **OAuth Guide:** https://developers.google.com/identity/protocols/oauth2

#### Streamlit
- **Documentation:** https://docs.streamlit.io/
- **API Reference:** https://docs.streamlit.io/library/api-reference

#### OpenAI
- **API Documentation:** https://platform.openai.com/docs/api-reference
- **Chat Completions:** https://platform.openai.com/docs/guides/chat

---

## 🔐 Security & Privacy

- OAuth 2.0 for secure calendar authentication
- API keys stored in environment variables
- Tokens encrypted and stored locally
- No sensitive data exposed in logs
- Session-based user isolation

---

## 🐛 Troubleshooting

### Common Issues

**1. Calendar Authentication Fails**
- Ensure `credentials.json` is in the correct location
- Check OAuth redirect URI matches configuration
- Verify Google Calendar API is enabled

**2. Memory Not Persisting**
- Check Mem0 API key is valid
- Verify internet connection
- Review Mem0 service status

**3. OpenAI API Errors**
- Validate API key
- Check rate limits
- Ensure sufficient credits

### Error Logs
Check `logs/chatbot.log` for detailed error information.

---
