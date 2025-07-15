from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    Numeric,
    Boolean,
    DateTime,
    text,
)
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from services.common.models.base import Base


class AuthMethod(PyEnum):
    NONE = "none"
    APIKEY = "apikey"
    TOKEN = "token"


class ChargeType(PyEnum):
    FREE = "free"
    PER_CALL = "per_call"
    PER_TOKEN = "per_token"


class McpService(Base):
    __tablename__ = "mcp_service"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    service_id = Column(
        String(36), unique=True, nullable=False, comment="Unique MCP service ID (UUID)"
    )
    name = Column(String(100), nullable=False, comment="Service name")
    slug_name = Column(
        String(100), unique=True, nullable=False, comment="Unique slug for the service"
    )
    short_description = Column(
        String(500), nullable=False, comment="Short service description"
    )
    long_description = Column(String, comment="Detailed description in Markdown")
    auth_method = Column(
        Enum(AuthMethod),
        nullable=False,
        default=AuthMethod.NONE,
        comment="Authentication method",
    )
    auth_header = Column(String(100), comment="Authentication header name")
    auth_token = Column(String(255), comment="Static authentication token")
    charge_type = Column(
        Enum(ChargeType),
        nullable=False,
        default=ChargeType.FREE,
        comment="Billing method",
    )
    price = Column(
        Numeric(10, 2), nullable=False, default=0.00, comment="Price per unit"
    )
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="Service status: 0=disabled, 1=enabled",
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
