from sqlalchemy import Column, BigInteger, String, Enum, Numeric, Integer, DateTime, text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from enum import Enum as PyEnum
from services.common.models.base import Base


class AuthMethod(PyEnum):
    FREE = "free"
    APIKEY = "apikey"
    TOKEN = "token"


class ChargeType(PyEnum):
    FREE = "free"
    PER_CALL = "per_call"
    PER_TOKEN = "per_token"


class McpService(Base):
    __tablename__ = "mcp_service"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    service_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, comment="MCP service unique ID (UUID format)"
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Service name"
    )
    slug_name: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, comment="Unique slug name for the service"
    )
    short_description: Mapped[str] = mapped_column(
        text.Text, nullable=False, comment="Short description of the service"
    )
    long_description: Mapped[str] = mapped_column(
        text.LongText, nullable=True, comment="Detailed description of the service (Markdown format)"
    )
    auth_method: Mapped[AuthMethod] = mapped_column(
        Enum(AuthMethod, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        comment="Authentication method: free, apikey, token",
    )
    auth_header: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="Authentication header name"
    )
    auth_token: Mapped[str] = mapped_column(
        String(255), nullable=True, comment="Authentication token value"
    )
    charge_type: Mapped[ChargeType] = mapped_column(
        Enum(ChargeType, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        comment="Charge type: free, per_call, per_token",
    )
    price: Mapped[float] = mapped_column(
        Numeric(10, 2), nullable=False, comment="Service price (2 decimal places)"
    )
    enabled: Mapped[int] = mapped_column(
        Integer, nullable=True, comment="Service status: 0=disabled, 1=enabled"
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