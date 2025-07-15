from sqlalchemy import (
    Column,
    BigInteger,
    String,
    Enum,
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    text,
)
from sqlalchemy.sql import func
from enum import Enum as PyEnum
from services.common.models.base import Base


class HttpMethod(PyEnum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class McpToolApi(Base):
    __tablename__ = "mcp_tool_api"

    id = Column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    tool_id = Column(
        String(36), unique=True, nullable=False, comment="Unique MCP tool ID (UUID)"
    )
    service_id = Column(
        String(36),
        ForeignKey("mcp_service.service_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
        comment="MCP service ID (UUID)",
    )
    name = Column(String(100), nullable=False, comment="API name")
    description = Column(String(500), nullable=False, comment="API description")
    url = Column(String(512), nullable=False, comment="API endpoint URL")
    method = Column(Enum(HttpMethod), nullable=False, comment="HTTP request method")
    headers = Column(JSON, comment="Request headers (JSON format)")
    params = Column(String, comment="Request parameters")
    request_body = Column(String, comment="Request body template")
    request_schema = Column(JSON, comment="Request schema (JSON)")
    response_schema = Column(JSON, comment="Response schema (JSON)")
    request_demo = Column(String, comment="Example request")
    response_demo = Column(String, comment="Example response")
    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
        comment="API status: 0=disabled, 1=enabled",
    )
    is_deleted = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Soft delete flag: 0=active, 1=deleted",
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
