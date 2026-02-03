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
    
    # Image Processing Configuration
    IMAGE_QUALITY = int(os.getenv("IMAGE_QUALITY")) if os.getenv("IMAGE_QUALITY") else None
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE")) if os.getenv("MAX_IMAGE_SIZE") else None
    
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
