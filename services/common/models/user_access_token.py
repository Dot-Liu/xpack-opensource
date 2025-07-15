from sqlalchemy import Column, BigInteger, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from services.common.models.base import Base


class UserAccessToken(Base):
    __tablename__ = "user_access_token"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    user_id: Mapped[str] = mapped_column(
        String(36), nullable=False, comment="User unique ID (UUID format)"
    )
    token: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="Access token"
    )
    expire_at: Mapped[DateTime] = mapped_column(
        DateTime, nullable=False, comment="Token expiration timestamp"
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime,
        nullable=True,
        server_default=func.current_timestamp(),
        comment="Creation timestamp",
    )