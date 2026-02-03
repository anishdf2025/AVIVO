import redis
import hashlib
import json
from typing import Optional
from ..core.config import Config
from ..core.logger import logger


class CacheService:
    """Service for handling Redis cache operations"""
    
    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                password=Config.REDIS_PASSWORD if Config.REDIS_PASSWORD else None,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.enabled = True
            logger.info(f"Redis cache connected: {Config.REDIS_HOST}:{Config.REDIS_PORT}")
        except Exception as e:
            self.enabled = False
            logger.warning(f"Redis cache disabled: {str(e)}")
    
    def generate_image_hash(self, image_data: bytes) -> str:
        """
        Generate a unique hash for image data
        
        Args:
            image_data: Raw image bytes
            
        Returns:
            SHA256 hash of the image
        """
        return hashlib.sha256(image_data).hexdigest()
    
    def get_cached_description(self, image_hash: str) -> Optional[str]:
        """
        Get cached description for an image
        
        Args:
            image_hash: Hash of the image
            
        Returns:
            Cached description or None if not found
        """
        if not self.enabled:
            return None
        
        try:
            cached = self.redis_client.get(f"image:{image_hash}")
            if cached:
                logger.info(f"Cache HIT for image hash: {image_hash[:16]}...")
                return cached
            logger.info(f"Cache MISS for image hash: {image_hash[:16]}...")
            return None
        except Exception as e:
            logger.error(f"Redis GET error: {str(e)}")
            return None
    
    def set_cached_description(self, image_hash: str, description: str) -> bool:
        """
        Cache image description
        
        Args:
            image_hash: Hash of the image
            description: Description to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            self.redis_client.setex(
                f"image:{image_hash}",
                Config.REDIS_TTL,
                description
            )
            logger.info(f"Cached description for hash: {image_hash[:16]}... (TTL: {Config.REDIS_TTL}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error: {str(e)}")
            return False
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            keys_count = self.redis_client.dbsize()
            return {
                "enabled": True,
                "keys_count": keys_count,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Redis stats error: {str(e)}")
            return {"enabled": True, "error": str(e)}
    
    def clear_cache(self) -> bool:
        """Clear all cached images"""
        if not self.enabled:
            return False
        
        try:
            pattern = "image:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Cleared {len(keys)} cached images")
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return False
