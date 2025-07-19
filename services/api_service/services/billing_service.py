"""
计费服务 - 处理用户API调用的计费逻辑
"""

import json
import uuid
import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from typing import Tuple, Optional
from contextlib import asynccontextmanager

from services.common.redis import redis_client
from services.common.rabbitmq import rabbitmq_client
from services.common.models.billing import BillingMessage, PreDeductResult, ApiCallLogInfo
from services.common.models.mcp_service import ChargeType
from services.common.models.user_wallet import UserWallet
from services.common.database import get_db
from services.api_service.repositories.mcp_service_repository import McpServiceRepository
from services.api_service.repositories.user_wallet_repository import UserWalletRepository
from services.common.logging_config import get_logger

logger = get_logger(__name__)


class BillingService:
    """计费服务类"""

    # 配置常量
    BILLING_LOCK_TIMEOUT = 5  # 分布式锁超时时间(秒)
    WALLET_CACHE_EXPIRE = 300  # 钱包缓存过期时间(秒)
    SERVICE_CACHE_EXPIRE = 3600  # 服务价格缓存过期时间(秒)
    BILLING_QUEUE_NAME = "billing.api.calls"

    def __init__(self):
        self.redis = redis_client
        self.rabbitmq = rabbitmq_client

    async def check_and_pre_deduct(self, user_id: str, service_id: str, tool_name: str) -> PreDeductResult:
        """
        检查余额并进行预扣费

        Args:
            user_id: 用户ID
            service_id: 服务ID
            tool_name: 工具名称

        Returns:
            PreDeductResult: 预扣费结果
        """
        try:
            # 获取服务价格信息
            service_price, charge_type = await self._get_service_price(service_id)

            # 免费服务直接放行
            if charge_type == ChargeType.FREE:
                logger.info(f"免费服务，跳过计费检查 - 用户ID: {user_id}, 服务ID: {service_id}")
                return PreDeductResult(success=True, message="免费服务", service_price=Decimal("0"), user_balance=Decimal("0"))

            # 获取分布式锁进行预扣费
            async with self._acquire_billing_lock(user_id):
                # 获取用户余额
                user_balance = await self._get_user_wallet_balance(user_id)

                # 检查余额是否充足
                if user_balance < service_price:
                    logger.warning(f"用户余额不足 - 用户ID: {user_id}, 余额: {user_balance}, 需要: {service_price}")
                    return PreDeductResult(
                        success=False,
                        message=f"余额不足，当前余额: {user_balance}，需要: {service_price}",
                        service_price=service_price,
                        user_balance=user_balance,
                    )

                # 在Redis中预扣费用
                new_balance = user_balance - service_price
                await self._update_wallet_cache(user_id, new_balance)

                logger.info(f"预扣费成功 - 用户ID: {user_id}, 扣费: {service_price}, 余额: {user_balance} -> {new_balance}")
                return PreDeductResult(success=True, message="预扣费成功", service_price=service_price, user_balance=new_balance)

        except Exception as e:
            logger.error(f"预扣费检查失败 - 用户ID: {user_id}, 服务ID: {service_id}: {str(e)}", exc_info=True)
            return PreDeductResult(success=False, message=f"系统异常: {str(e)}", service_price=Decimal("0"), user_balance=Decimal("0"))

    async def send_billing_message(self, call_log: ApiCallLogInfo, call_success: bool, call_end_time: datetime) -> None:
        """
        发送计费消息到RabbitMQ

        Args:
            call_log: API调用记录信息
            call_success: 调用是否成功
            call_end_time: 调用结束时间
        """
        try:
            message = BillingMessage(
                user_id=call_log.user_id,
                service_id=call_log.service_id,
                api_id=call_log.api_id,
                tool_name=call_log.tool_name,
                input_params=call_log.input_params,
                call_success=call_success,
                unit_price=call_log.unit_price,
                call_start_time=call_log.call_start_time,
                call_end_time=call_end_time,
            )

            # 序列化消息
            message_json = json.dumps(
                {
                    "user_id": message.user_id,
                    "service_id": message.service_id,
                    "api_id": message.api_id,
                    "tool_name": message.tool_name,
                    "input_params": message.input_params,
                    "call_success": message.call_success,
                    "unit_price": str(message.unit_price),
                    "call_start_time": message.call_start_time.isoformat(),
                    "call_end_time": message.call_end_time.isoformat() if message.call_end_time else None,
                }
            )

            # 发送到RabbitMQ
            self.rabbitmq.publish(self.BILLING_QUEUE_NAME, message_json)
            logger.info(f"计费消息发送成功 - 用户ID: {call_log.user_id}, 工具: {call_log.tool_name}")

        except Exception as e:
            logger.error(f"发送计费消息失败: {str(e)}", exc_info=True)
            # 这里可以考虑将失败的消息保存到本地队列，后续重试

    async def _get_service_price(self, service_id: str) -> Tuple[Decimal, ChargeType]:
        """
        获取服务价格和计费类型

        Args:
            service_id: 服务ID

        Returns:
            Tuple[Decimal, ChargeType]: 价格和计费类型
        """
        # 尝试从Redis缓存获取
        cache_key = f"service:price:{service_id}"
        cached_data = self.redis.get(cache_key)

        if cached_data:
            try:
                data = json.loads(cached_data)
                return Decimal(data["price"]), ChargeType(data["charge_type"])
            except (json.JSONDecodeError, KeyError, ValueError):
                logger.warning(f"服务价格缓存数据异常，从数据库重新获取 - 服务ID: {service_id}")

        # 从数据库获取
        db = next(get_db())
        try:
            service_repo = McpServiceRepository(db)
            service = service_repo.get_by_id(service_id)

            if not service:
                raise ValueError(f"服务不存在: {service_id}")

            price = Decimal(str(service.price))
            charge_type = service.charge_type

            # 缓存到Redis
            cache_data = {"price": str(price), "charge_type": charge_type.value}
            self.redis.set(cache_key, json.dumps(cache_data), ex=self.SERVICE_CACHE_EXPIRE)

            return price, charge_type

        finally:
            db.close()

    async def _get_user_wallet_balance(self, user_id: str) -> Decimal:
        """
        获取用户钱包余额

        Args:
            user_id: 用户ID

        Returns:
            Decimal: 用户余额
        """
        # 尝试从Redis缓存获取
        cache_key = f"wallet:balance:{user_id}"
        cached_balance = self.redis.get(cache_key)

        if cached_balance:
            try:
                return Decimal(cached_balance)
            except (ValueError, TypeError):
                logger.warning(f"钱包余额缓存数据异常，从数据库重新获取 - 用户ID: {user_id}")

        # 从数据库获取
        db = next(get_db())
        try:
            wallet_repo = UserWalletRepository(db)
            wallet = wallet_repo.get_by_user_id(user_id)

            if not wallet:
                # 用户钱包不存在，创建一个新的
                wallet = wallet_repo.create(user_id)
                logger.info(f"为用户创建新钱包 - 用户ID: {user_id}")

            balance = Decimal(str(wallet.balance))

            # 缓存到Redis
            self.redis.set(cache_key, str(balance), ex=self.WALLET_CACHE_EXPIRE)

            return balance

        finally:
            db.close()

    async def _update_wallet_cache(self, user_id: str, new_balance: Decimal) -> None:
        """
        更新钱包余额缓存

        Args:
            user_id: 用户ID
            new_balance: 新余额
        """
        cache_key = f"wallet:balance:{user_id}"
        self.redis.set(cache_key, str(new_balance), ex=self.WALLET_CACHE_EXPIRE)

    @asynccontextmanager
    async def _acquire_billing_lock(self, user_id: str):
        """
        获取计费分布式锁

        Args:
            user_id: 用户ID

        Yields:
            锁上下文
        """
        lock_key = f"billing:lock:{user_id}"
        lock_value = str(uuid.uuid4())

        try:
            # 尝试获取锁 (使用Redis SET命令的NX和EX选项)
            lua_script = """
            return redis.call('SET', KEYS[1], ARGV[1], 'NX', 'EX', ARGV[2])
            """
            acquired = self.redis.client.eval(lua_script, 1, lock_key, lock_value, str(self.BILLING_LOCK_TIMEOUT))
            if not acquired:
                raise Exception(f"无法获取计费锁，用户可能有其他操作在进行 - 用户ID: {user_id}")

            logger.debug(f"获取计费锁成功 - 用户ID: {user_id}")
            yield

        finally:
            # 释放锁（只有持有锁的进程才能释放）
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            self.redis.client.eval(lua_script, 1, lock_key, lock_value)
            logger.debug(f"释放计费锁 - 用户ID: {user_id}")


# 全局实例
billing_service = BillingService()
