from sqlalchemy import Column, BigInteger, String, Numeric, DateTime, ForeignKey, text
from sqlalchemy.sql import func
from services.common.models.base import Base


class UserWallet(Base):
    __tablename__ = "user_wallet"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    user_id = Column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="User ID (UUID)",
    )
    balance = Column(
        Numeric(10, 2), nullable=False, default=0.00, comment="Wallet balance"
    )
    frozen_balance = Column(
        Numeric(10, 2), nullable=False, default=0.00, comment="Frozen balance"
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
