from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import base64
from pathlib import Path
from ..services.vision_service import VisionService
from ..services.cache_service import CacheService
from ..core.logger import logger
from ..core.config import Config

router = APIRouter()
vision_service = VisionService()
cache_service = CacheService()


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
        
        # Validate file size
        content = await file.read()
        if len(content) > Config.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {Config.MAX_IMAGE_SIZE} bytes"
            )
        
        # Check cache first
        image_hash = cache_service.generate_image_hash(content)
        cached = cache_service.get_cached_description(image_hash)
        
        if cached:
            logger.info(f"Returning cached result for {file.filename}")
            return JSONResponse(content={
                "success": True,
                "filename": file.filename,
                "description": cached,
                "cached": True
            })
        
        # Save temp file
        temp_path = Config.TEMP_DIR / f"api_{file.filename}"
        
        with open(temp_path, "wb") as buffer:
            buffer.write(content)
        
        # Get description with timeout handling
        try:
            description = vision_service.describe_image(str(temp_path))
        except Exception as e:
            if "timed out" in str(e).lower():
                raise HTTPException(
                    status_code=504, 
                    detail="Request timeout. The model took too long to process the image."
                )
            raise
        
        # Cleanup
        temp_path.unlink()
        
        logger.info(f"API request processed for file: {file.filename}")
        
        return JSONResponse(content={
            "success": True,
            "filename": file.filename,
            "description": description,
            "cached": False
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/cache/stats")
async def get_cache_stats():
    """Get Redis cache statistics"""
    return cache_service.get_cache_stats()


@router.delete("/api/cache/clear")
async def clear_cache():
    """Clear all cached images"""
    success = cache_service.clear_cache()
    if success:
        return {"message": "Cache cleared successfully"}
    raise HTTPException(status_code=500, detail="Failed to clear cache")
