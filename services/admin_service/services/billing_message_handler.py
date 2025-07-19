"""
计费消息处理服务
"""
import json
import uuid
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session

from services.common.models.billing import BillingMessage
from services.common.models.mcp_call_log import McpCallLog, ProcessStatus
from services.common.models.user_wallet_history import UserWalletHistory, TransactionType, PaymentMethod
from services.admin_service.repositories.mcp_call_log_repository import McpCallLogRepository
from services.admin_service.repositories.user_wallet_repository import UserWalletRepository
from services.admin_service.repositories.user_wallet_history_repository import UserWalletHistoryRepository
from services.common.redis import redis_client

logger = logging.getLogger(__name__)


class BillingMessageHandler:
    """计费消息处理器"""
    
    def __init__(self, db: Session):
        self.db = db
        self.call_log_repo = McpCallLogRepository(db)
        self.wallet_repo = UserWalletRepository(db)
        self.wallet_history_repo = UserWalletHistoryRepository(db)
        self.redis = redis_client
    
    def process_billing_message(self, message_data: dict) -> bool:
        """
        处理计费消息
        
        Args:
            message_data: 消息数据
            
        Returns:
            bool: 处理是否成功
        """
        try:
            # Parse message
            billing_message = self._parse_message(message_data)
            if not billing_message:
                return False
            
            # Create API call log
            call_log_id = self._create_call_log(billing_message)
            if not call_log_id:
                return False
            
            # Process billing logic
            if billing_message.call_success and billing_message.unit_price > 0:
                success = self._process_billing(billing_message, call_log_id)
                if not success:
                    # Update record status to failed
                    self.call_log_repo.update_status(call_log_id, ProcessStatus.FAILED, "Billing processing failed")
                    return False
            
            # Update record status to processed
            self.call_log_repo.update_status(call_log_id, ProcessStatus.PROCESSED)
            logger.info(f"Billing message processed successfully - User ID: {billing_message.user_id}, Tool: {billing_message.tool_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process billing message: {str(e)}", exc_info=True)
            return False
    
    def _parse_message(self, message_data: dict) -> Optional[BillingMessage]:
        """
        解析RabbitMQ消息
        
        Args:
            message_data: 消息数据
            
        Returns:
            Optional[BillingMessage]: 解析后的计费消息
        """
        try:
            call_start_time = datetime.fromisoformat(message_data["call_start_time"].replace('Z', '+00:00'))
            call_end_time = None
            if message_data.get("call_end_time"):
                call_end_time = datetime.fromisoformat(message_data["call_end_time"].replace('Z', '+00:00'))
            
            return BillingMessage(
                user_id=message_data["user_id"],
                service_id=message_data["service_id"],
                api_id=message_data["api_id"],
                tool_name=message_data["tool_name"],
                input_params=message_data["input_params"],
                call_success=message_data["call_success"],
                unit_price=Decimal(message_data["unit_price"]),
                call_start_time=call_start_time,
                call_end_time=call_end_time,
                apikey=message_data.get("apikey")  # 支持旧版本消息没有该字段的情况
            )
        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"消息解析失败: {str(e)}, 消息内容: {message_data}")
            return None
    
    def _create_call_log(self, billing_message: BillingMessage) -> Optional[str]:
        """
        创建API调用记录
        
        Args:
            billing_message: 计费消息
            
        Returns:
            Optional[str]: 创建的记录ID
        """
        try:
            log_id = str(uuid.uuid4())
            call_log = McpCallLog(
                id=log_id,
                user_id=billing_message.user_id,
                service_id=billing_message.service_id,
                api_id=billing_message.api_id,
                tool_name=billing_message.tool_name,
                input_params=billing_message.input_params,
                call_success=billing_message.call_success,
                unit_price=float(billing_message.unit_price),
                actual_cost=0.0,  # 初始为0，后续更新
                call_start_time=billing_message.call_start_time,
                call_end_time=billing_message.call_end_time,
                process_status=ProcessStatus.PENDING,
                apikey=billing_message.apikey
            )
            
            created_log = self.call_log_repo.create(call_log)
            return created_log.id
            
        except Exception as e:
            logger.error(f"创建API调用记录失败: {str(e)}")
            return None
    
    def _process_billing(self, billing_message: BillingMessage, call_log_id: str) -> bool:
        """
        处理实际计费逻辑
        
        Args:
            billing_message: 计费消息
            call_log_id: 调用记录ID
            
        Returns:
            bool: 处理是否成功
        """
        try:
            user_id = billing_message.user_id
            amount = billing_message.unit_price
            
            # 获取用户钱包
            wallet = self.wallet_repo.get_by_user_id(user_id)
            if not wallet:
                logger.error(f"用户钱包不存在 - 用户ID: {user_id}")
                return False
            
            current_balance = Decimal(str(wallet.balance))
            
            # 检查余额是否充足（理论上已经预扣过了，但这里再次检查确保数据一致性）
            if current_balance < amount:
                logger.warning(f"用户余额不足，无法完成扣费 - 用户ID: {user_id}, 余额: {current_balance}, 需要: {amount}")
                return False
            
            # 执行扣费
            new_balance = current_balance - amount
            success = self.wallet_repo.update_balance(user_id, float(new_balance))
            if not success:
                logger.error(f"更新用户钱包余额失败 - 用户ID: {user_id}")
                return False
            
            # 创建钱包变更历史记录
            history_id = str(uuid.uuid4())
            wallet_history = UserWalletHistory(
                id=history_id,
                user_id=user_id,
                payment_method=PaymentMethod.PLATFORM,
                amount=float(-amount),  # 负数表示扣费
                balance_after=float(new_balance),
                type=TransactionType.API_CALL,
                status=1,  # 已完成
                transaction_id=call_log_id,
                channel_user_id=None
            )
            
            created_history = self.wallet_history_repo.add_consume_record(wallet_history)
            if not created_history:
                logger.error(f"创建钱包变更历史失败 - 用户ID: {user_id}")
                # 回滚余额更新
                self.wallet_repo.update_balance(user_id, float(current_balance))
                return False
            
            # 更新API调用记录的实际扣费金额和关联历史记录ID
            self.call_log_repo.update_status(call_log_id, ProcessStatus.PROCESSED, None, history_id)
            
            # 更新Redis缓存中的钱包余额
            self._update_wallet_cache(user_id, new_balance)
            
            logger.info(f"计费处理成功 - 用户ID: {user_id}, 扣费: {amount}, 余额: {current_balance} -> {new_balance}")
            return True
            
        except Exception as e:
            logger.error(f"计费处理失败 - 用户ID: {billing_message.user_id}: {str(e)}", exc_info=True)
            return False
    
    def _update_wallet_cache(self, user_id: str, new_balance: Decimal) -> None:
        """
        更新Redis中的钱包余额缓存
        
        Args:
            user_id: 用户ID
            new_balance: 新余额
        """
        try:
            cache_key = f"wallet:balance:{user_id}"
            self.redis.set(cache_key, str(new_balance), ex=300)  # 5分钟过期
        except Exception as e:
            logger.warning(f"更新钱包缓存失败 - 用户ID: {user_id}: {str(e)}")
            # 缓存更新失败不影响主流程
