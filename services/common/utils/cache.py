"""
缓存工具模块
提供通用的Redis缓存操作方法
"""

import json
import logging
from typing import Optional, Any
from objtyping import to_primitive
from services.common.redis import redis_client

logger = logging.getLogger(__name__)

# 默认缓存过期时间
DEFAULT_CACHE_EXPIRE_TIME = 3600  # 1小时


def get_model_cache(cache_key: str, model_class: type) -> Optional[Any]:
    """
    获取缓存
    """
    try:
        # 从Redis缓存获取
        cache_value = redis_client.get(cache_key)
        if cache_value:
            return model_class(**json.loads(cache_value))
        return None
    except Exception as e:
        logger.error(f"Cache/DB operation failed for key {cache_key}: {e}")
        return None


def get_cache(cache_key: str) -> Optional[Any]:
    """
    获取缓存
    """
    try:
        # 从Redis缓存获取
        return redis_client.get(cache_key)
    except Exception as e:
        logger.error(f"Cache/DB operation failed for key {cache_key}: {e}")
        return None


def set_cache(key: str, value: Any, expire_time: int = DEFAULT_CACHE_EXPIRE_TIME) -> bool:
    """
    设置缓存

    Args:
        key: 缓存键
        value: 缓存值
        expire_time: 过期时间（秒）

    Returns:
        是否设置成功
    """
    try:
        redis_client.set(key, value, ex=expire_time)
        return True
    except Exception as e:
        logger.error(f"Failed to set cache for key {key}: {e}")
        return False


def set_model_cache(cache_key: str, model: Any, expire_time: int = DEFAULT_CACHE_EXPIRE_TIME) -> bool:
    """
    设置缓存
    """
    try:
        redis_client.set(cache_key, json.dumps(to_primitive(model)), ex=expire_time)
        return True
    except Exception as e:
        logger.error(f"Failed to set cache for key {cache_key}: {e}")
        return False


def delete_cache(key: str) -> bool:
    """
    删除缓存

    Args:
        key: 缓存键

    Returns:
        是否删除成功
    """
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        logger.error(f"Failed to delete cache for key {key}: {e}")
        return False


def clear_pattern_cache(pattern: str) -> int:
    """
    清除匹配模式的缓存

    Args:
        pattern: 缓存键模式（如 "xpack:user:*"）

    Returns:
        删除的缓存数量
    """
    try:
        # 注意：这里需要根据实际的Redis客户端实现来调整
        # 如果Redis客户端支持scan操作，可以使用scan来查找匹配的键
        logger.warning("Pattern cache clearing not implemented - use specific keys instead")
        return 0
    except Exception as e:
        logger.error(f"Failed to clear pattern cache for {pattern}: {e}")
        return 0
