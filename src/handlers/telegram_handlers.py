import os
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from ..services.vision_service import VisionService
from ..core.config import Config
from ..core.logger import logger


class TelegramHandlers:
    """Handlers for Telegram bot commands and messages"""
    
    def __init__(self):
        self.vision_service = VisionService()
        self.temp_dir = Config.TEMP_DIR
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        logger.info(f"User {user.id} ({user.username}) started the bot")
        
        welcome_message = (
            f"👋 Hello {user.first_name}!\n\n"
            "I'm an AI-powered image description bot using Qwen Vision Model.\n\n"
            "📸 Just send me any image and I'll describe it in detail!\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - Get help information"
        )
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "ℹ️ How to use:\n\n"
            "1. Send me any image (photo, screenshot, etc.)\n"
            "2. Wait a few seconds while I analyze it\n"
            "3. Get a detailed description!\n\n"
            "💡 Tips:\n"
            "• Higher quality images = better descriptions\n"
            "• The bot works with JPG, PNG, and other formats\n"
            "• Processing may take 5-30 seconds depending on image size"
        )
        
        await update.message.reply_text(help_message)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages"""
        user = update.effective_user
        photo = update.message.photo[-1]  # Get highest quality photo
        
        logger.info(f"Received photo from user {user.id} ({user.username})")
        
        await update.message.reply_text("🔄 Processing your image... Please wait.")
        
        # Create temp file path
        temp_path = self.temp_dir / f"temp_{photo.file_id}.jpg"
        
        try:
            # Download the photo
            file = await context.bot.get_file(photo.file_id)
            await file.download_to_drive(temp_path)
            logger.info(f"Downloaded photo to {temp_path}")
            
            # Get description
            description = self.vision_service.describe_image(str(temp_path))
            
            # Send response
            response_message = f"🧠 **Image Description:**\n\n{description}"
            await update.message.reply_text(response_message)
            
            logger.info(f"Successfully processed image for user {user.id}")
            
        except Exception as e:
            error_message = f"❌ Sorry, I encountered an error processing your image.\n\nError: {str(e)}"
            await update.message.reply_text(error_message)
            logger.error(f"Error processing image for user {user.id}: {str(e)}")
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
                logger.info(f"Cleaned up temp file: {temp_path}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document messages (images sent as files)"""
        document = update.message.document
        
        # Check if it's an image
        if document.mime_type and document.mime_type.startswith('image/'):
            await self.handle_photo(update, context)
        else:
            await update.message.reply_text(
                "📎 Please send images as photos, not documents, for better results."
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An unexpected error occurred. Please try again later."
            )
