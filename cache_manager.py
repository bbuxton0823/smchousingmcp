"""Cache manager for storing and retrieving data."""

import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Optional, Dict
from pathlib import Path
import structlog

from config.settings import settings
from models import CacheEntry

logger = structlog.get_logger()


class CacheManager:
    """Cache manager for storing and retrieving data."""
    
    def __init__(self):
        self.cache_dir = Path.home() / ".smcgov_housing_cache"
        self.cache_dir.mkdir(exist_ok=True)
        self._memory_cache: Dict[str, CacheEntry] = {}
        self._redis_client = None
        
        # Initialize Redis if available
        if settings.redis_url:
            try:
                import redis
                self._redis_client = redis.from_url(settings.redis_url)
                logger.info("Redis cache initialized")
            except ImportError:
                logger.warning("Redis not available, using file cache only")
            except Exception as e:
                logger.warning("Failed to connect to Redis", error=str(e))
    
    async def get(self, key: str) -> Optional[Any]:
        """Get data from cache."""
        try:
            # Check memory cache first
            if key in self._memory_cache:
                entry = self._memory_cache[key]
                if entry.expires_at > datetime.now():
                    logger.debug("Cache hit (memory)", key=key)
                    return entry.data
                else:
                    del self._memory_cache[key]
            
            # Check Redis cache
            if self._redis_client:
                try:
                    cached_data = self._redis_client.get(key)
                    if cached_data:
                        entry = pickle.loads(cached_data)
                        if entry.expires_at > datetime.now():
                            # Store in memory cache for faster access
                            self._memory_cache[key] = entry
                            logger.debug("Cache hit (Redis)", key=key)
                            return entry.data
                        else:
                            self._redis_client.delete(key)
                except Exception as e:
                    logger.warning("Redis get failed", key=key, error=str(e))
            
            # Check file cache
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    expires_at = datetime.fromisoformat(cache_data['expires_at'])
                    if expires_at > datetime.now():
                        data = cache_data['data']
                        # Store in memory cache
                        entry = CacheEntry(
                            key=key,
                            data=data,
                            expires_at=expires_at
                        )
                        self._memory_cache[key] = entry
                        logger.debug("Cache hit (file)", key=key)
                        return data
                    else:
                        cache_file.unlink()
                except Exception as e:
                    logger.warning("File cache read failed", key=key, error=str(e))
            
            logger.debug("Cache miss", key=key)
            return None
            
        except Exception as e:
            logger.error("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, data: Any, ttl_hours: Optional[int] = None) -> bool:
        """Set data in cache."""
        try:
            if ttl_hours is None:
                ttl_hours = settings.cache_ttl_hours
            
            expires_at = datetime.now() + timedelta(hours=ttl_hours)
            entry = CacheEntry(
                key=key,
                data=data,
                expires_at=expires_at
            )
            
            # Store in memory cache
            self._memory_cache[key] = entry
            
            # Store in Redis cache
            if self._redis_client:
                try:
                    serialized = pickle.dumps(entry)
                    ttl_seconds = int(ttl_hours * 3600)
                    self._redis_client.setex(key, ttl_seconds, serialized)
                    logger.debug("Cached in Redis", key=key, ttl_hours=ttl_hours)
                except Exception as e:
                    logger.warning("Redis set failed", key=key, error=str(e))
            
            # Store in file cache
            try:
                cache_data = {
                    'key': key,
                    'data': data,
                    'expires_at': expires_at.isoformat(),
                    'created_at': datetime.now().isoformat()
                }
                
                cache_file = self.cache_dir / f"{key}.json"
                with open(cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2, default=str)
                
                logger.debug("Cached in file", key=key, ttl_hours=ttl_hours)
            except Exception as e:
                logger.warning("File cache write failed", key=key, error=str(e))
            
            return True
            
        except Exception as e:
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete data from cache."""
        try:
            # Remove from memory cache
            if key in self._memory_cache:
                del self._memory_cache[key]
            
            # Remove from Redis cache
            if self._redis_client:
                try:
                    self._redis_client.delete(key)
                except Exception as e:
                    logger.warning("Redis delete failed", key=key, error=str(e))
            
            # Remove from file cache
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
            
            logger.debug("Cache deleted", key=key)
            return True
            
        except Exception as e:
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    async def clear(self) -> bool:
        """Clear all cache data."""
        try:
            # Clear memory cache
            self._memory_cache.clear()
            
            # Clear Redis cache
            if self._redis_client:
                try:
                    # Get all keys with our prefix
                    keys = self._redis_client.keys("smcgov_housing:*")
                    if keys:
                        self._redis_client.delete(*keys)
                except Exception as e:
                    logger.warning("Redis clear failed", error=str(e))
            
            # Clear file cache
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            
            logger.info("Cache cleared")
            return True
            
        except Exception as e:
            logger.error("Cache clear failed", error=str(e))
            return False
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            stats = {
                'memory_cache_size': len(self._memory_cache),
                'file_cache_size': len(list(self.cache_dir.glob("*.json"))),
                'redis_available': self._redis_client is not None
            }
            
            if self._redis_client:
                try:
                    redis_info = self._redis_client.info()
                    stats['redis_memory_usage'] = redis_info.get('used_memory_human', 'unknown')
                    stats['redis_keys'] = len(self._redis_client.keys("smcgov_housing:*"))
                except Exception as e:
                    logger.warning("Failed to get Redis stats", error=str(e))
                    stats['redis_error'] = str(e)
            
            return stats
            
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return {}
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a cache key from prefix and parameters."""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}:{v}")
        return "smcgov_housing:" + ":".join(key_parts)


# Global cache manager instance
cache_manager = CacheManager()

