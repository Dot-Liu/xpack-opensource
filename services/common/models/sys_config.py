from sqlalchemy import Column, BigInteger, String, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from services.common.models.base import Base


class SysConfig(Base):
    __tablename__ = "sys_config"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    key: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="Configuration key"
    )
    value: Mapped[str] = mapped_column(
        text.Text, nullable=False, comment="Configuration value"
    )
    description: Mapped[str] = mapped_column(
        text.Text, nullable=False, comment="Configuration description"
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
        comment="Creation timestamp",
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="Last update timestamp",
    )