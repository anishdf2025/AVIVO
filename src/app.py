from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from .api.routes import router
from .bot import AvivoBot
from .core.logger import logger


# Global bot instance
bot_instance = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    global bot_instance
    
    # Startup
    logger.info("Starting Avivo application...")
    
    # Start Telegram bot in background
    bot_instance = AvivoBot()
    bot_instance.setup()
    
    # Run bot in background task
    asyncio.create_task(run_bot())
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Avivo application...")
    if bot_instance and bot_instance.app:
        await bot_instance.app.stop()
    logger.info("Application shutdown complete")


async def run_bot():
    """Run the Telegram bot"""
    try:
        if bot_instance and bot_instance.app:
            await bot_instance.app.initialize()
            await bot_instance.app.start()
            await bot_instance.app.updater.start_polling(allowed_updates=["message"])
            
            # Keep running
            while True:
                await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Bot error: {str(e)}")


# Create FastAPI app
app = FastAPI(
    title="Avivo - AI Image Description Bot",
    description="Telegram bot with API for AI-powered image descriptions",
    version="1.0.0",
    lifespan=lifespan
)

# Include routes
app.include_router(router)
