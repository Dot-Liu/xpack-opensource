from sqlalchemy import Column, BigInteger, String, ForeignKey, TIMESTAMP
from sqlalchemy.sql import func
from services.common.models.base import Base


class UserAccessToken(Base):
    __tablename__ = "user_access_token"

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
    token = Column(String(255), unique=True, nullable=False, comment="Access token")
    expire_at = Column(TIMESTAMP, nullable=False, comment="Token expiration timestamp")
    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=func.current_timestamp(),
        comment="Creation timestamp",
    )
