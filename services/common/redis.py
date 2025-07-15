import redis
from typing import Optional, Any
from .config import Config


class RedisClient:
    """Redis客户端封装类，提供基本的Redis操作功能"""
    
    def __init__(self):
        """初始化Redis连接"""
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
            # 测试连接
            self.client.ping()
        except redis.ConnectionError as e:
            raise ConnectionError(f"无法连接到Redis服务器: {e}")
        except Exception as e:
            raise Exception(f"Redis初始化失败: {e}")

    def set(self, key: str, value: str, ex: Optional[int] = None) -> Any:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值
            ex: 过期时间（秒），None表示永不过期
            
        Returns:
            Any: 操作结果
        """
        try:
            return self.client.set(key, value, ex=ex)
        except redis.RedisError as e:
            raise Exception(f"Redis SET操作失败: {e}")

    def get(self, key: str) -> Any:
        """
        获取键值
        
        Args:
            key: 键名
            
        Returns:
            Any: 值，如果键不存在则返回None
        """
        try:
            result = self.client.get(key)
            return result if result is not None else None
        except redis.RedisError as e:
            raise Exception(f"Redis GET操作失败: {e}")

    def delete(self, key: str) -> Any:
        """
        删除键
        
        Args:
            key: 键名
            
        Returns:
            Any: 删除的键数量
        """
        try:
            return self.client.delete(key)
        except redis.RedisError as e:
            raise Exception(f"Redis DELETE操作失败: {e}")

    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 键名
            
        Returns:
            bool: 键是否存在
        """
        try:
            result = self.client.exists(key)
            return bool(result)
        except redis.RedisError as e:
            raise Exception(f"Redis EXISTS操作失败: {e}")

    def expire(self, key: str, seconds: int) -> Any:
        """
        设置键的过期时间
        
        Args:
            key: 键名
            seconds: 过期时间（秒）
            
        Returns:
            Any: 操作结果
        """
        try:
            return self.client.expire(key, seconds)
        except redis.RedisError as e:
            raise Exception(f"Redis EXPIRE操作失败: {e}")

    def ttl(self, key: str) -> Any:
        """
        获取键的剩余过期时间
        
        Args:
            key: 键名
            
        Returns:
            Any: 剩余秒数，-1表示永不过期，-2表示键不存在
        """
        try:
            return self.client.ttl(key)
        except redis.RedisError as e:
            raise Exception(f"Redis TTL操作失败: {e}")

    def close(self):
        """关闭Redis连接"""
        try:
            self.client.close()
        except Exception as e:
            # 忽略关闭时的错误
            pass

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 全局Redis客户端实例
redis_client = RedisClient()
