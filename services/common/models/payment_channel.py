from sqlalchemy import String, Text, DateTime,Integer
from sqlalchemy.orm import Mapped, mapped_column
from services.common.models.base import Base
from datetime import datetime


class PaymentChannel(Base):
    __tablename__ = "payment_channel"
    """
    CREATE TABLE `payment_channel` (
    `id` char(36) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '支付渠道唯一ID',
    `name` varchar(255) DEFAULT NULL COMMENT '渠道名称',
    `status` tinyint DEFAULT NULL COMMENT '渠道状态，0:未启用，1已启用',
    `config` text COMMENT '配置信息',
    `update_at` timestamp NULL DEFAULT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
    """
    id: Mapped[str] = mapped_column(String(36), primary_key=True, autoincrement=False, comment="Primary key")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Channel name")
    status: Mapped[int] = mapped_column(Integer, nullable=False, comment="Channel status, 0: disabled, 1: enabled")
    config: Mapped[str] = mapped_column(Text, nullable=True, comment="Channel config")
    update_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, comment="Update time")
