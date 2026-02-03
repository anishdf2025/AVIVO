"""
Avivo - Telegram Image Description Bot
Main entry point for the application
"""

import uvicorn
from src.core.logger import logger
from src.core.config import Config


def main():
    """Main function to run the application"""
    try:
        logger.info("🚀 Starting Avivo application with uvicorn...")
        
        uvicorn.run(
            "src.app:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
        
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
