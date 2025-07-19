"""
计费相关的数据模型
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass
class BillingMessage:
    """RabbitMQ计费消息模型"""
    user_id: str
    service_id: str
    api_id: str
    tool_name: str
    input_params: str
    call_success: bool
    unit_price: Decimal
    call_start_time: datetime
    call_end_time: Optional[datetime] = None
    call_log_id: Optional[str] = None


@dataclass
class ApiCallLogInfo:
    """API调用记录信息"""
    user_id: str
    service_id: str
    api_id: str
    tool_name: str
    input_params: str
    unit_price: Decimal
    call_start_time: datetime
    call_end_time: Optional[datetime] = None


@dataclass
class PreDeductResult:
    """预扣费结果"""
    success: bool
    message: str
    service_price: Decimal
    user_balance: Decimal
