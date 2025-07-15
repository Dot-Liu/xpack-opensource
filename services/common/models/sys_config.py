from sqlalchemy import Column, BigInteger, String, DateTime, text
from sqlalchemy.sql import func
from services.common.models.base import Base


class SysConfig(Base):
    __tablename__ = "sys_config"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    key = Column(String(100), unique=True, nullable=False, comment="Configuration key")
    value = Column(String, nullable=False, comment="Configuration value")
    description = Column(
        String(500), nullable=False, comment="Configuration description"
    )
    created_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Creation timestamp",
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="Last update timestamp",
    )
