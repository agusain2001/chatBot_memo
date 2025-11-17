"""
Configuration Settings Module
Central configuration management for the chatbot application.

All API keys and sensitive data should be stored in .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / 'data'
LOGS_DIR = BASE_DIR / 'logs'

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)


class Config:
    """Main configuration class."""
    
    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'Student Schedule Assistant')
    DEBUG_MODE = os.getenv('DEBUG_MODE', 'False').lower() == 'true'
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4')
    OPENAI_TEMPERATURE = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
    OPENAI_MAX_TOKENS = int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    
    # Anthropic Configuration (Alternative)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')
    
    # Mem0 Configuration
    # Citation: Mem0 configuration - https://docs.mem0.ai/configuration
    MEM0_API_KEY = os.getenv('MEM0_API_KEY')
    MEM0_ORG_ID = os.getenv('MEM0_ORG_ID')
    
    MEM0_CONFIG = {
        "vector_store": {
            "provider": "qdrant",
            "config": {
                "collection_name": os.getenv('MEM0_COLLECTION', 'student_memories'),
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
    
    # Google Calendar Configuration
    # Citation: Google OAuth - https://developers.google.com/identity/protocols/oauth2
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8501')
    
    GOOGLE_SCOPES = [
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    # Calendar file paths
    CREDENTIALS_FILE = BASE_DIR / 'credentials.json'
    TOKEN_FILE = BASE_DIR / 'token.pickle'
    
    # MCP Configuration
    MCP_SERVER_URL = os.getenv('MCP_SERVER_URL', 'http://localhost:3000')
    
    # Database Configuration
    DB_PATH = DATA_DIR / 'chatbot.db'
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = LOGS_DIR / 'chatbot.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Session Configuration
    SESSION_SECRET = os.getenv('SESSION_SECRET', 'your-secret-key-change-in-production')
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))  # 1 hour
    
    # Chatbot Settings
    MAX_CONVERSATION_HISTORY = int(os.getenv('MAX_CONVERSATION_HISTORY', '10'))
    MAX_MEMORY_RESULTS = int(os.getenv('MAX_MEMORY_RESULTS', '10'))
    MAX_CALENDAR_EVENTS = int(os.getenv('MAX_CALENDAR_EVENTS', '50'))
    
    # Feature Flags
    ENABLE_MEMORY = os.getenv('ENABLE_MEMORY', 'True').lower() == 'true'
    ENABLE_CALENDAR = os.getenv('ENABLE_CALENDAR', 'True').lower() == 'true'
    ENABLE_NLP = os.getenv('ENABLE_NLP', 'True').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate that all required configuration is present.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        required_vars = []
        
        # Check OpenAI or Anthropic key
        if not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            required_vars.append('OPENAI_API_KEY or ANTHROPIC_API_KEY')
        
        # Check Mem0 configuration if memory is enabled
        if cls.ENABLE_MEMORY and not cls.MEM0_API_KEY:
            required_vars.append('MEM0_API_KEY')
        
        # Check Google Calendar configuration if calendar is enabled
        if cls.ENABLE_CALENDAR:
            if not cls.CREDENTIALS_FILE.exists():
                required_vars.append('credentials.json file')
        
        if required_vars:
            print("❌ Missing required configuration:")
            for var in required_vars:
                print(f"   - {var}")
            return False
        
        print("✅ Configuration validated successfully")
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)."""
        print("\n" + "="*60)
        print("CURRENT CONFIGURATION")
        print("="*60)
        print(f"App Name: {cls.APP_NAME}")
        print(f"Debug Mode: {cls.DEBUG_MODE}")
        print(f"OpenAI Model: {cls.OPENAI_MODEL}")
        print(f"Memory Enabled: {cls.ENABLE_MEMORY}")
        print(f"Calendar Enabled: {cls.ENABLE_CALENDAR}")
        print(f"NLP Enabled: {cls.ENABLE_NLP}")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print(f"Max Conversation History: {cls.MAX_CONVERSATION_HISTORY}")
        print("="*60 + "\n")


class DevelopmentConfig(Config):
    """Development-specific configuration."""
    DEBUG_MODE = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production-specific configuration."""
    DEBUG_MODE = False
    LOG_LEVEL = 'WARNING'
    
    # More restrictive settings for production
    MAX_CONVERSATION_HISTORY = 5
    OPENAI_TEMPERATURE = 0.5


class TestConfig(Config):
    """Testing-specific configuration."""
    DEBUG_MODE = True
    LOG_LEVEL = 'DEBUG'
    
    # Use test database
    DB_PATH = DATA_DIR / 'test_chatbot.db'
    
    # Disable external API calls in tests
    ENABLE_MEMORY = False
    ENABLE_CALENDAR = False


# Determine which config to use based on environment
ENV = os.getenv('ENVIRONMENT', 'development').lower()

if ENV == 'production':
    config = ProductionConfig()
elif ENV == 'testing':
    config = TestConfig()
else:
    config = DevelopmentConfig()


# Logging setup
import logging

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format=config.LOG_FORMAT,
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# Utility functions
def get_config():
    """Get the current configuration object."""
    return config


def get_logger(name: str = __name__):
    """
    Get a logger instance.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


# Export commonly used items
__all__ = [
    'Config',
    'DevelopmentConfig',
    'ProductionConfig',
    'TestConfig',
    'config',
    'logger',
    'get_config',
    'get_logger',
    'BASE_DIR',
    'DATA_DIR',
    'LOGS_DIR'
]


# Validate configuration on import
if __name__ != "__main__":
    config.validate()
else:
    # If run directly, print configuration
    config.print_config()
    config.validate()