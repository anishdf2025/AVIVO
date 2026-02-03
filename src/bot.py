from telegram.ext import Application, CommandHandler, MessageHandler, filters
from .core.config import Config
from .core.logger import logger
from .handlers.telegram_handlers import TelegramHandlers


class AvivoBot:
    """Main bot application class"""
    
    def __init__(self):
        self.config = Config
        self.handlers = TelegramHandlers()
        self.app = None
    
    def setup(self):
        """Setup bot application and handlers"""
        logger.info("Setting up Avivo bot...")
        
        # Create application
        self.app = Application.builder().token(self.config.TELEGRAM_BOT_TOKEN).build()
        
        # Add command handlers
        self.app.add_handler(CommandHandler("start", self.handlers.start_command))
        self.app.add_handler(CommandHandler("help", self.handlers.help_command))
        
        # Add message handlers
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handlers.handle_photo))
        self.app.add_handler(MessageHandler(filters.Document.IMAGE, self.handlers.handle_document))
        
        # Add error handler
        self.app.add_error_handler(self.handlers.error_handler)
        
        logger.info("Bot setup completed successfully")
    
    def run(self):
        """Run the bot"""
        if not self.app:
            self.setup()
        
        logger.info("🤖 Avivo bot is running... Send images to get descriptions!")
        logger.info(f"Using model: {self.config.OLLAMA_MODEL}")
        
        # Start polling
        self.app.run_polling(allowed_updates=["message"])
