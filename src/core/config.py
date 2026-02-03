import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration class"""
    
    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # Ollama Configuration
    OLLAMA_URL = os.getenv("OLLAMA_URL")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")
    OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT")) if os.getenv("OLLAMA_TIMEOUT") else None
    
    # Image Processing Configuration
    IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY")) if os.getenv("IMAGE_QUALITY") else None
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE")) if os.getenv("MAX_IMAGE_SIZE") else None
    
    # API Configuration
    API_TIMEOUT = int(os.getenv("API_TIMEOUT")) if os.getenv("API_TIMEOUT") else None
    
    # Redis Configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_TTL = int(os.getenv("REDIS_TTL", "86400"))  # 24 hours default
    
    # Paths
    TEMP_DIR = BASE_DIR / "temp"
    LOGS_DIR = BASE_DIR / "logs"
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_fields = {
            "TELEGRAM_BOT_TOKEN": cls.TELEGRAM_BOT_TOKEN,
            "OLLAMA_URL": cls.OLLAMA_URL,
            "OLLAMA_MODEL": cls.OLLAMA_MODEL,
            "IMAGE_QUALITY": cls.IMAGE_QUALITY,
            "MAX_IMAGE_SIZE": cls.MAX_IMAGE_SIZE,
            "OLLAMA_TIMEOUT": cls.OLLAMA_TIMEOUT,
            "API_TIMEOUT": cls.API_TIMEOUT,
        }
        
        missing = [field for field, value in required_fields.items() if not value]
        
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")
        
        # Create necessary directories
        cls.TEMP_DIR.mkdir(exist_ok=True)
        cls.LOGS_DIR.mkdir(exist_ok=True)
        
        return True


# Validate configuration on import
Config.validate()
