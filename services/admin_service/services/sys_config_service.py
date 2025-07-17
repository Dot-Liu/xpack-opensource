from sqlalchemy.orm import Session
from typing import Optional
from services.common.database import SessionLocal
from services.common.redis import RedisClient
from services.common.redis_keys import RedisKeys
import logging

from services.common.models.sys_config import SysConfig
from services.admin_service.repositories.sys_config_repository import SysConfigRepository

logger = logging.getLogger(__name__)


class SysConfigService:
    def __init__(self, db: Session = SessionLocal()):
        self.sys_config_repository = SysConfigRepository(db)
        try:
            self.redis_client = RedisClient()
        except Exception as e:
            logger.warning(f"Redis connection failed, cache will be disabled: {e}")
            self.redis_client = None

    def get_value_by_key(self, key: str) -> Optional[str]:
        """
        获取配置值，优先从缓存获取，缓存不存在则从数据库获取并缓存

        Args:
            key: 配置key

        Returns:
            Optional[str]: 配置值，不存在返回None
        """
        # 生成缓存key
        cache_key = RedisKeys.sys_config_key(key)

        # 先尝试从Redis获取
        if self.redis_client:
            try:
                cached_value = self.redis_client.get(cache_key)
                if cached_value is not None:
                    logger.debug(f"Got sys_config {key} from cache")
                    # 特殊处理空值缓存
                    return None if cached_value == "__NULL__" else cached_value
            except Exception as e:
                logger.warning(f"Failed to get cache for key {key}: {e}")

        # 从数据库获取
        try:
            value = self.sys_config_repository.get_value_by_key(key)

            # 缓存结果（包括空值）
            if self.redis_client:
                try:
                    # 空值用特殊标记缓存，避免缓存穿透
                    cache_value = "__NULL__" if value is None else value
                    # 缓存1小时（3600秒）
                    self.redis_client.set(cache_key, cache_value, ex=3600)
                    logger.debug(f"Cached sys_config {key} for 1 hour")
                except Exception as e:
                    logger.warning(f"Failed to cache key {key}: {e}")

            return value
        except Exception as e:
            logger.error(f"Failed to get sys_config {key} from database: {e}")
            return None

    def delete_by_key(self, key: str) -> bool:
        """删除配置并清除缓存"""
        result = self.sys_config_repository.delete_by_key(key)
        if result:
            self._clear_cache(key)
        return result

    def set_value_by_key(self, key: str, value: str, description: str) -> Optional[SysConfig]:
        """设置配置值并清除缓存"""
        result = self.sys_config_repository.set_value_by_key(key=key, value=value, description=description)
        if result:
            self._clear_cache(key)
        return result

    def _clear_cache(self, key: str) -> None:
        """清除指定配置的缓存"""
        if self.redis_client:
            try:
                cache_key = RedisKeys.sys_config_key(key)
                self.redis_client.delete(cache_key)
                logger.debug(f"Cleared cache for sys_config {key}")
            except Exception as e:
                logger.warning(f"Failed to clear cache for key {key}: {e}")

    def get_multiple_values(self, keys: list[str]) -> dict[str, Optional[str]]:
        """
        批量获取配置值，优化多个配置同时获取的性能

        Args:
            keys: 配置key列表

        Returns:
            dict[str, Optional[str]]: key-value映射字典
        """
        result = {}
        cache_miss_keys = []

        # 先尝试从Redis逐个获取（由于没有mget方法）
        if self.redis_client and keys:
            for key in keys:
                try:
                    cache_key = RedisKeys.sys_config_key(key)
                    cached_value = self.redis_client.get(cache_key)
                    if cached_value is not None:
                        # 处理空值标记
                        result[key] = None if cached_value == "__NULL__" else cached_value
                        logger.debug(f"Got sys_config {key} from cache")
                    else:
                        cache_miss_keys.append(key)
                except Exception as e:
                    logger.warning(f"Failed to get cache for key {key}: {e}")
                    cache_miss_keys.append(key)
        else:
            cache_miss_keys = keys

        # 从数据库获取缓存未命中的配置
        if cache_miss_keys:
            try:
                for key in cache_miss_keys:
                    value = self.sys_config_repository.get_value_by_key(key)
                    result[key] = value

                    # 缓存结果
                    if self.redis_client:
                        try:
                            cache_key = RedisKeys.sys_config_key(key)
                            cache_value = "__NULL__" if value is None else value
                            self.redis_client.set(cache_key, cache_value, ex=3600)
                            logger.debug(f"Cached sys_config {key} for 1 hour")
                        except Exception as e:
                            logger.warning(f"Failed to cache key {key}: {e}")
            except Exception as e:
                logger.error(f"Failed to get sys_config from database: {e}")
                # 为未成功获取的key设置None
                for key in cache_miss_keys:
                    if key not in result:
                        result[key] = None

        return result
