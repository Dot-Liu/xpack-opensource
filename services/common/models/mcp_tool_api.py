from sqlalchemy import Column, BigInteger, String, Enum, Integer, DateTime, JSON, text
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
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

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="Primary key, auto-incremented ID",
    )
    tool_id: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, comment="MCP tool unique ID (UUID format)"
    )
    service_id: Mapped[str] = mapped_column(
        String(36), nullable=False, comment="Associated MCP service unique ID (UUID format)"
    )
    name: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="API name"
    )
    description: Mapped[str] = mapped_column(
        text.Text, nullable=False, comment="API function description"
    )
    url: Mapped[str] = mapped_column(
        String(512), nullable=False, comment="API request URL"
    )
    method: Mapped[HttpMethod] = mapped_column(
        Enum(HttpMethod, values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
        comment="HTTP request method",
    )
    headers: Mapped[dict] = mapped_column(
        JSON, nullable=True, comment="Request headers (JSON format)"
    )
    params: Mapped[str] = mapped_column(
        text.LongText, nullable=True, comment="Request parameters definition"
    )
    request_body: Mapped[str] = mapped_column(
        text.LongText, nullable=True, comment="Request body content"
    )
    request_schema: Mapped[dict] = mapped_column(
        JSON, nullable=True, comment="Request body schema (JSON Schema format)"
    )
    response_schema: Mapped[dict] = mapped_column(
        JSON, nullable=True, comment="Response body schema (JSON Schema format)"
    )
    request_demo: Mapped[str] = mapped_column(
        text.LongText, nullable=True, comment="Request example"
    )
    response_demo: Mapped[str] = mapped_column(
        text.LongText, nullable=True, comment="Response example"
    )
    enabled: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="API status: 0=disabled, 1=enabled"
    )
    is_deleted: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, comment="Soft delete flag: 0=active, 1=deleted"
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