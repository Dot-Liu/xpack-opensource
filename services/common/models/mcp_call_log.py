"""
MCP调用记录模型
"""

from sqlalchemy import String, Text, Boolean, Numeric, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from services.common.models.base import Base


class ProcessStatus(PyEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    FAILED = "failed"


class McpCallLog(Base):
    __tablename__ = "mcp_call_log"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        autoincrement=False,
        comment="UUID主键",
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="用户ID")
    service_id: Mapped[str] = mapped_column(String(36), nullable=False, comment="MCP服务ID")
    api_id: Mapped[str] = mapped_column(String(100), nullable=False, comment="API工具ID")
    tool_name: Mapped[str] = mapped_column(String(200), nullable=False, comment="工具名称")
    input_params: Mapped[str] = mapped_column(Text, nullable=True, comment="调用参数")
    apikey_id: Mapped[str] = mapped_column(String(36), nullable=True, comment="API密钥ID")
    call_success: Mapped[int] = mapped_column(Boolean, nullable=False, comment="调用是否成功")
    unit_price: Mapped[float] = mapped_column(Numeric(10, 4), nullable=False, comment="单次调用价格")
    actual_cost: Mapped[float] = mapped_column(Numeric(10, 4), nullable=True, default=0.0000, comment="实际扣费金额")
    call_start_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, comment="调用开始时间")
    call_end_time: Mapped[DateTime] = mapped_column(DateTime, nullable=True, comment="调用结束时间")
    process_status: Mapped[ProcessStatus] = mapped_column(
        Enum(ProcessStatus, values_callable=lambda obj: [e.value for e in obj]),
        nullable=True,
        default=ProcessStatus.PENDING,
        comment="处理状态: pending, processed, failed",
    )
    error_msg: Mapped[str] = mapped_column(Text, nullable=True, comment="错误信息")
    wallet_history_id: Mapped[str] = mapped_column(String(36), nullable=True, comment="关联的钱包变更记录ID")
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
        comment="创建时间",
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新时间",
    )
