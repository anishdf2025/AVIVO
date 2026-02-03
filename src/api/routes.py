from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import base64
from pathlib import Path
from ..services.vision_service import VisionService
from ..core.logger import logger
from ..core.config import Config

router = APIRouter()
vision_service = VisionService()


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Avivo - AI Image Description Bot",
        "version": "1.0.0",
        "status": "running"
    }


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": Config.OLLAMA_MODEL,
        "ollama_url": Config.OLLAMA_URL
    }


@router.post("/api/describe")
async def describe_image(file: UploadFile = File(...)):
    """
    API endpoint to describe uploaded image
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save temp file
        temp_path = Config.TEMP_DIR / f"api_{file.filename}"
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Get description
        description = vision_service.describe_image(str(temp_path))
        
        # Cleanup
        temp_path.unlink()
        
        logger.info(f"API request processed for file: {file.filename}")
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "description": description
        })
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/stats")
async def get_stats():
    """Get bot statistics"""
    return {
        "model": Config.OLLAMA_MODEL,
        "image_quality": Config.IMAGE_QUALITY,
        "max_image_size": Config.MAX_IMAGE_SIZE
    }
