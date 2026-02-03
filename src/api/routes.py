from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import base64
from pathlib import Path
from ..services.vision_service import VisionService
from ..services.cache_service import CacheService
from ..services.rag_service import RAGService
from ..core.logger import logger
from ..core.config import Config

router = APIRouter()
vision_service = VisionService()
cache_service = CacheService()
rag_service = RAGService()


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
    """API endpoint to describe uploaded image"""
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
        
        # Get description
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


# RAG Endpoints (Simplified)

@router.post("/api/rag/upload")
async def upload_to_rag(file: UploadFile = File(...)):
    """Upload a document to RAG knowledge base"""
    try:
        # Save uploaded file temporarily
        temp_path = Config.TEMP_DIR / file.filename
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Add to RAG
        metadata = {
            'source': 'api',
            'filename': file.filename,
            'file_size': len(content)
        }
        success = rag_service.add_document_from_file(temp_path, metadata)
        
        # Cleanup
        temp_path.unlink()
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to process document")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Document '{file.filename}' added to knowledge base",
            "filename": file.filename
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/rag/query")
async def rag_query(question: str, top_k: int = None):
    """Query RAG system (answer only, no sources)"""
    try:
        if not question or len(question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question cannot be empty")
        
        # Query without sources
        result = rag_service.query(question, top_k=top_k, include_sources=False)
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG query error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/rag/clear")
async def clear_rag():
    """Clear RAG knowledge base"""
    try:
        success = rag_service.vector_store.clear()  # ← USAGE #2
        
        if success:
            return {"message": "Knowledge base cleared successfully"}
        raise HTTPException(status_code=500, detail="Failed to clear knowledge base")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"RAG clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/cache/clear")
async def clear_cache(cache_type: str = "all"):
    """
    Clear Redis cache
    
    Args:
        cache_type: 'all', 'images', or 'rag'
    """
    try:
        if cache_type not in ["all", "images", "rag"]:
            raise HTTPException(
                status_code=400, 
                detail="cache_type must be 'all', 'images', or 'rag'"
            )
        
        success = cache_service.clear_cache(cache_type)
        
        if success:
            return {
                "message": f"Cleared {cache_type} cache successfully",
                "cache_type": cache_type
            }
        raise HTTPException(status_code=500, detail="Failed to clear cache")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cache clear error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    return cache_service.get_cache_stats()


@router.get("/api/rag/stats")
async def rag_stats():
    """Get RAG system statistics"""
    return rag_service.get_stats()
