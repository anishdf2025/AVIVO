import redis
import hashlib
import json
from typing import Optional
from ..core.config import Config
from ..core.logger import logger


class CacheService:
    """Service for handling Redis cache operations (Images + RAG)"""
    
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
    
    # ==================== IMAGE CACHING ====================
    
    def generate_image_hash(self, image_data: bytes) -> str:
        """Generate a unique hash for image data"""
        return hashlib.sha256(image_data).hexdigest()
    
    def get_cached_description(self, image_hash: str) -> Optional[str]:
        """Get cached description for an image"""
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
        """Cache image description"""
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
    
    # ==================== RAG QUERY CACHING ====================
    
    def generate_rag_cache_key(self, query: str) -> str:
        """
        Generate cache key for RAG query
        
        Args:
            query: User's question
            
        Returns:
            Cache key (rag_query:hash)
        """
        # Normalize query for better cache hits
        normalized = query.lower().strip()
        hash_obj = hashlib.sha256(normalized.encode())
        return f"rag_query:{hash_obj.hexdigest()}"
    
    def get_cached_rag_response(self, query: str) -> Optional[dict]:
        """
        Get cached RAG response
        
        Args:
            query: User's question
            
        Returns:
            Cached response dict or None
        """
        if not self.enabled:
            return None
        
        try:
            cache_key = self.generate_rag_cache_key(query)
            cached_result = self.redis_client.get(cache_key)
            
            if cached_result:
                logger.info(f"✅ Cache HIT for RAG query: {query[:30]}...")
                return json.loads(cached_result)
            else:
                logger.info(f"❌ Cache MISS for RAG query: {query[:30]}...")
                return None
        except Exception as e:
            logger.error(f"Cache read error: {str(e)}")
            return None
    
    def set_cached_rag_response(self, query: str, response: dict, ttl: int = 3600) -> bool:
        """
        Cache RAG response
        
        Args:
            query: User's question
            response: Response dict to cache
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            True if cached successfully
        """
        if not self.enabled:
            return False
        
        try:
            cache_key = self.generate_rag_cache_key(query)
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(response)
            )
            logger.info(f"💾 Cached RAG response for query: {query[:30]}...")
            return True
        except Exception as e:
            logger.error(f"Cache write error: {str(e)}")
            return False
    
    # ==================== CACHE MANAGEMENT ====================
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}
        
        try:
            info = self.redis_client.info()
            
            # Count different key types
            image_keys = len(self.redis_client.keys("image:*"))
            rag_keys = len(self.redis_client.keys("rag_query:*"))
            total_keys = self.redis_client.dbsize()
            
            return {
                "enabled": True,
                "total_keys": total_keys,
                "image_keys": image_keys,
                "rag_query_keys": rag_keys,
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0)
            }
        except Exception as e:
            logger.error(f"Redis stats error: {str(e)}")
            return {"enabled": True, "error": str(e)}
    
    def clear_cache(self, cache_type: str = "all") -> bool:
        """
        Clear cached data
        
        Args:
            cache_type: 'all', 'images', or 'rag'
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return False
        
        try:
            if cache_type == "all":
                self.redis_client.flushdb()
                logger.info("Cleared all cached data")
            elif cache_type == "images":
                keys = self.redis_client.keys("image:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cached images")
            elif cache_type == "rag":
                keys = self.redis_client.keys("rag_query:*")
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"Cleared {len(keys)} cached RAG queries")
            
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {str(e)}")
            return False
