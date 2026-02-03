import os
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes
from ..services.vision_service import VisionService
from ..services.rag_service import RAGService
from ..core.config import Config
from ..core.logger import logger


class TelegramHandlers:
    """Handlers for Telegram bot commands and messages"""
    
    def __init__(self):
        self.vision_service = VisionService()
        self.rag_service = RAGService()
        self.temp_dir = Config.TEMP_DIR
        self.max_message_length = 4096
    
    def split_message(self, text: str, max_length: int = 4096) -> list:
        """
        Split long message into chunks
        
        Args:
            text: Message text to split
            max_length: Maximum length per message
            
        Returns:
            List of message chunks
        """
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) + 2 <= max_length:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = ""
                
                # If single paragraph is too long, split by sentences
                if len(paragraph) > max_length:
                    sentences = paragraph.split('. ')
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 2 <= max_length:
                            current_chunk += sentence + ". "
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + ". "
                else:
                    current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
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
            "📸 Image Analysis:\n"
            "• Send any image to get a detailed description\n\n"
            "💬 RAG Q&A (LangChain + FAISS):\n"
            "• Ask questions directly (auto-detected)\n"
            "• Upload documents (PDF, DOCX, TXT, etc.)\n"
            "• /clearrag - Clear knowledge base\n\n"
            "📊 Other Commands:\n"
            "• /start - Show welcome message\n"
            "• /help - Show this help\n"
            "• /stats - Show system statistics\n\n"
            "💡 Tips:\n"
            "• Higher quality images = better descriptions\n"
            "• Semantic search powered by LangChain FAISS"
        )
        
        await update.message.reply_text(help_message)
    
    async def ask_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ask command for RAG queries"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                "❓ Please provide a question!\n\n"
                "Usage: /ask <your question>\n"
                "Example: /ask What is machine learning?"
            )
            return
        
        question = ' '.join(context.args)
        logger.info(f"RAG query: {question[:50]}...")  # ← REMOVED user ID
        
        await update.message.reply_text("🔍 Searching knowledge base...")
        
        try:
            result = self.rag_service.query(question, include_sources=False)
            answer = result.get('answer', 'No answer found.')
            
            response = f"💡 **Answer:**\n\n{answer}"
            message_chunks = self.split_message(response, self.max_message_length - 50)
            
            for i, chunk in enumerate(message_chunks):
                if i == 0:
                    await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(f"📄 (continued)\n\n{chunk}")
            
        except Exception as e:
            error_msg = f"❌ Error processing your question: {str(e)[:200]}"
            await update.message.reply_text(error_msg)
            logger.error(f"RAG query error: {str(e)}")
    
    async def addtext_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addtext command to add text to RAG knowledge base"""
        user = update.effective_user
        
        if not context.args:
            await update.message.reply_text(
                "📝 Please provide text to add!\n\n"
                "Usage: /addtext <your text>\n"
                "Example: /addtext Machine learning is a subset of AI"
            )
            return
        
        text = ' '.join(context.args)
        logger.info("Adding text to RAG")  # ← REMOVED user ID
        
        await update.message.reply_text("💾 Adding to knowledge base...")
        
        try:
            metadata = {
                'source': 'telegram',
                'user_id': user.id,
                'username': user.username or 'unknown'
            }
            
            success = self.rag_service.add_document(text, metadata)
            
            if success:
                await update.message.reply_text(
                    "✅ Text added to knowledge base successfully!\n\n"
                    "You can now ask questions about it using /ask"
                )
                logger.info(f"Text added to RAG by user {user.id}")
            else:
                await update.message.reply_text(
                    "❌ Failed to add text to knowledge base"
                )
                
        except Exception as e:
            error_msg = f"❌ Error adding text: {str(e)[:200]}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error adding text for user {user.id}: {str(e)}")
    
    async def clearrag_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /clearrag command to clear RAG knowledge base"""
        user = update.effective_user
        logger.info(f"Clear RAG request from user {user.id}")
        
        try:
            success = self.rag_service.vector_store.clear()  # ← USAGE #1
            
            if success:
                await update.message.reply_text(
                    "🗑️ RAG knowledge base cleared successfully!"
                )
                logger.info(f"RAG cleared by user {user.id}")
            else:
                await update.message.reply_text(
                    "❌ Failed to clear knowledge base"
                )
                
        except Exception as e:
            error_msg = f"❌ Error clearing knowledge base: {str(e)[:200]}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error clearing RAG for user {user.id}: {str(e)}")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command to show system statistics"""
        user = update.effective_user
        logger.info(f"Stats request from user {user.id}")
        
        try:
            rag_stats = self.rag_service.get_stats()
            
            stats_message = (
                "📊 **System Statistics**\n\n"
                f"🤖 Vision Model: {Config.OLLAMA_MODEL}\n"
                f"🧠 RAG Model: {rag_stats.get('llm_model', 'N/A')}\n"
                f"📚 Documents: {rag_stats.get('vector_store', {}).get('total_documents', 0)}\n"
                f"🔢 Embedding Dim: {rag_stats.get('vector_store', {}).get('embedding_dimension', 0)}\n"
                f"🎯 Similarity Threshold: {rag_stats.get('similarity_threshold', 0)}\n"
                f"📦 Top K Results: {rag_stats.get('top_k', 0)}"
            )
            
            await update.message.reply_text(stats_message)
            
        except Exception as e:
            error_msg = f"❌ Error getting stats: {str(e)[:200]}"
            await update.message.reply_text(error_msg)
            logger.error(f"Error getting stats for user {user.id}: {str(e)}")
    
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
            
            # Split long messages
            message_chunks = self.split_message(description, self.max_message_length - 50)
            
            # Send response (split if needed)
            if len(message_chunks) == 1:
                response_message = f"🧠 **Image Description:**\n\n{description}"
                await update.message.reply_text(response_message)
            else:
                # Send first part with header
                await update.message.reply_text(f"🧠 **Image Description (Part 1/{len(message_chunks)}):**\n\n{message_chunks[0]}")
                
                # Send remaining parts
                for i, chunk in enumerate(message_chunks[1:], start=2):
                    await update.message.reply_text(f"📄 **Part {i}/{len(message_chunks)}:**\n\n{chunk}")
            
            logger.info(f"Successfully processed image for user {user.id}")
            
        except Exception as e:
            error_message = f"❌ Sorry, I encountered an error processing your image.\n\nError: {str(e)[:200]}"
            await update.message.reply_text(error_message)
            logger.error(f"Error processing image for user {user.id}: {str(e)}")
            
        finally:
            # Clean up temporary file
            if temp_path.exists():
                temp_path.unlink()
                logger.info(f"Cleaned up temp file: {temp_path}")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document messages (PDFs, Word files, etc.)"""
        user = update.effective_user
        document = update.message.document
        
        logger.info(f"📄 Received document from user {user.id}: {document.file_name}")
        
        # Check if it's an image
        if document.mime_type and document.mime_type.startswith('image/'):
            logger.info(f"Document is an image, redirecting to handle_photo")
            await self.handle_photo(update, context)
            return
        
        # Get file extension
        file_ext = Path(document.file_name).suffix.lower()
        logger.info(f"📋 Document extension: {file_ext}")
        
        # Check if it's a supported document
        try:
            supported_formats = self.rag_service.doc_loader.get_supported_formats()
            logger.info(f"✅ Supported formats: {supported_formats}")
            
            if file_ext not in supported_formats:
                await update.message.reply_text(
                    f"❌ Unsupported file format: {file_ext}\n\n"
                    f"Supported formats: {', '.join(supported_formats)}\n\n"
                    f"Please send: PDF, DOCX, TXT, XLSX, or PPTX files"
                )
                return
        except Exception as e:
            logger.error(f"❌ Error checking supported formats: {str(e)}", exc_info=True)
            await update.message.reply_text(f"❌ Error: {str(e)[:200]}")
            return
        
        # Send initial processing message
        processing_msg = await update.message.reply_text(
            "📄 **Processing Document**\n\n"
            "⏳ Step 1/4: Downloading..."
        )
        
        # Download the document
        temp_path = self.temp_dir / document.file_name
        
        try:
            logger.info(f"⬇️ Downloading document to {temp_path}")
            file = await context.bot.get_file(document.file_id)
            await file.download_to_drive(temp_path)
            logger.info(f"✅ Downloaded document successfully: {temp_path}")
            
            # Verify file exists and has content
            if not temp_path.exists():
                raise Exception("Downloaded file does not exist")
            
            file_size = temp_path.stat().st_size
            logger.info(f"📦 Downloaded file size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("Downloaded file is empty")
            
            # Update: Loading content
            await processing_msg.edit_text(
                "📄 **Processing Document**\n\n"
                "✅ Step 1/4: Downloaded\n"
                "⏳ Step 2/4: Loading content..."
            )
            
            # Add to RAG
            metadata = {
                'source': 'telegram',
                'user_id': user.id,
                'username': user.username or 'unknown',
                'original_filename': document.file_name,
                'file_size': file_size
            }
            
            logger.info(f"📚 Loading document with metadata: {metadata}")
            
            # Update: Parsing
            await processing_msg.edit_text(
                "📄 **Processing Document**\n\n"
                "✅ Step 1/4: Downloaded\n"
                "✅ Step 2/4: Content loaded\n"
                "⏳ Step 3/4: Parsing and chunking..."
            )
            
            success = self.rag_service.add_document_from_file(temp_path, metadata)
            
            # Update: Creating embeddings
            await processing_msg.edit_text(
                "📄 **Processing Document**\n\n"
                "✅ Step 1/4: Downloaded\n"
                "✅ Step 2/4: Content loaded\n"
                "✅ Step 3/4: Parsed and chunked\n"
                "⏳ Step 4/4: Creating embeddings and storing..."
            )
            
            if success:
                # Get stats to show how many chunks were added
                stats = self.rag_service.get_stats()
                doc_count = stats.get('vector_store', {}).get('total_documents', 0)
                
                await processing_msg.edit_text(
                    f"✅ **Document Added Successfully!**\n\n"
                    f"📄 File: {document.file_name}\n"
                    f"📦 Size: {file_size / 1024:.1f} KB\n"
                    f"📚 Total documents in knowledge base: {doc_count}\n\n"
                    f"💡 You can now ask questions using:\n"
                    f"/ask <your question>"
                )
                logger.info(f"✅ Document added to RAG successfully by user {user.id}")
            else:
                await processing_msg.edit_text(
                    "❌ **Failed to Process Document**\n\n"
                    "The document could not be parsed or added to the knowledge base.\n"
                    "Please check the logs for details or try a different file."
                )
                logger.error(f"❌ Failed to add document to RAG for user {user.id}")
            
        except Exception as e:
            error_message = (
                f"❌ **Error Processing Document**\n\n"
                f"File: {document.file_name}\n"
                f"Error: {str(e)[:150]}\n\n"
                f"Please try again or contact support if the issue persists."
            )
            await processing_msg.edit_text(error_message)
            logger.error(f"❌ Error processing document for user {user.id}: {str(e)}", exc_info=True)
            
        finally:
            # Clean up
            if temp_path.exists():
                try:
                    temp_path.unlink()
                    logger.info(f"🧹 Cleaned up temp file: {temp_path}")
                except Exception as e:
                    logger.error(f"⚠️ Error cleaning up temp file: {str(e)}")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle plain text messages - Auto-detect questions and query RAG"""
        user = update.effective_user
        text = update.message.text
        
        if text.startswith('/'):
            return
        
        # Check if it's a question
        question_indicators = ['?', 'what', 'who', 'when', 'where', 'why', 'how', 'tell me', 'can you']
        is_question = any(indicator in text.lower() for indicator in question_indicators)
        
        if is_question and len(text.split()) > 3:  # At least 3 words
            logger.info(f"🔍 Detected question")
            await update.message.reply_text("🔍 Let me search the knowledge base...")
            
            try:
                result = self.rag_service.query(text, include_sources=False)
                answer = result.get('answer', 'No answer found.')
                
                if 'no relevant information' in answer.lower():
                    response = (
                        "⚠️ **No information found in knowledge base**\n\n"
                        "Please upload documents using file upload or use:\n"
                        "/addtext <information>"
                    )
                else:
                    response = f"💡 **Answer:**\n\n{answer}"
                
                message_chunks = self.split_message(response, self.max_message_length - 50)
                
                for i, chunk in enumerate(message_chunks):
                    if i == 0:
                        await update.message.reply_text(chunk)
                    else:
                        await update.message.reply_text(f"📄 (continued)\n\n{chunk}")
                
            except Exception as e:
                error_msg = f"❌ Error: {str(e)[:200]}"
                await update.message.reply_text(error_msg)
                logger.error(f"❌ RAG query error: {str(e)}")
        else:
            # Not a question - show help
            await update.message.reply_text(
                "💬 I received your message!\n\n"
                "💡 **Ask me questions** (I'll search automatically)\n"
                "Example: What is the name in the resume?\n\n"
                "📸 **Send images** for AI description\n"
                "📄 **Send documents** (PDF, DOCX) to add to knowledge base\n\n"
                "Or use commands:\n"
                "• /ask <question> - Ask questions\n"
                "• /addtext <info> - Add information\n"
                "• /help - See all commands"
            )
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ An unexpected error occurred. Please try again later."
            )
