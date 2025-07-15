from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    Numeric,
    Integer,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from services.common.models.base import Base


class PaymentMethod(PyEnum):
    PLATFORM = "platform"
    STRIPE = "stripe"
    ALIPAY = "alipay"
    WECHAT = "wechat"


class TransactionType(PyEnum):
    DEPOSIT = "deposit"
    CONSUME = "consume"
    REFUND = "refund"


class UserWalletHistory(Base):
    __tablename__ = "user_wallet_history"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    history_id = Column(
        String(36),
        unique=True,
        nullable=False,
        comment="Unique transaction history ID (UUID)",
    )
    user_id = Column(
        String(36),
        ForeignKey("user.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="User ID (UUID)",
    )
    payment_method = Column(
        Enum(PaymentMethod), nullable=False, comment="Payment method"
    )
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Transaction amount (positive=deposit, negative=consumption)",
    )
    balance_after = Column(
        Numeric(10, 2), nullable=False, comment="Balance after transaction"
    )
    type = Column(Enum(TransactionType), nullable=False, comment="Transaction type")
    status = Column(
        Integer,
        nullable=False,
        comment="Transaction status: 0=new, 1=completed, 2=pending",
    )
    transaction_id = Column(
        String(255), unique=True, comment="Payment platform transaction ID"
    )
    channel_user_id = Column(String(255), comment="Payment channel user ID")
    callback_data = Column(String, comment="Payment callback data")
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
