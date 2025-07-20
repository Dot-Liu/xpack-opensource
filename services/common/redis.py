import redis
from typing import Optional, Any
from .config import Config


class RedisClient:
    """Redis client wrapper providing basic Redis operations"""
    
    def __init__(self):
        """Initialize Redis connection"""
        try:
            self.client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                password=Config.REDIS_PASSWORD,
                db=Config.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            # Test connection
            self.client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"Cannot connect to Redis server: {e}")
        except Exception as e:
            raise Exception(f"Redis initialization failed: {e}")

    def set(self, key: str, value: str, ex: Optional[int] = None) -> Any:
        """Set key-value pair"""
        try:
            return self.client.set(key, value, ex=ex)
        except redis.RedisError as e:
            raise Exception(f"Redis SET operation failed: {e}")

    def get(self, key: str) -> Any:
        """Get value by key"""
        try:
            result = self.client.get(key)
            return result if result is not None else None
        except redis.RedisError as e:
            raise Exception(f"Redis GET operation failed: {e}")

    def delete(self, key: str) -> Any:
        """Delete key"""
        try:
            return self.client.delete(key)
        except redis.RedisError as e:
            raise Exception(f"Redis DELETE operation failed: {e}")

    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            result = self.client.exists(key)
            return bool(result)
        except redis.RedisError as e:
            raise Exception(f"Redis EXISTS operation failed: {e}")

    def expire(self, key: str, seconds: int) -> Any:
        """Set key expiration time"""
        try:
            return self.client.expire(key, seconds)
        except redis.RedisError as e:
            raise Exception(f"Redis EXPIRE operation failed: {e}")

    def ttl(self, key: str) -> Any:
        """Get remaining TTL for key"""
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            raise Exception(f"Redis TTL operation failed: {e}")

    def close(self):
        """Close Redis connection"""
        try:
            self.client.close()
        except Exception as e:
            # Ignore close errors
            pass

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Global Redis client instance
redis_client = RedisClient()
