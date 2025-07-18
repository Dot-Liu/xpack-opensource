from sqlalchemy.orm import Session
from services.common.models.mcp_tool_api import McpToolApi
from typing import Optional


class McpToolApiRepository:
    def __init__(self, db: Session):
        self.db = db

    def update(self, mcp_tool_api: McpToolApi) -> McpToolApi:
        db_obj = self.db.query(McpToolApi).filter(McpToolApi.id == mcp_tool_api.id).first()
        if not db_obj:
            raise ValueError("McpToolApi not found")
        db_obj.name = mcp_tool_api.name
        db_obj.description = mcp_tool_api.description
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def create(self, mcp_tool_api: McpToolApi) -> McpToolApi:
        self.db.add(mcp_tool_api)
        self.db.commit()
        self.db.refresh(mcp_tool_api)
        return mcp_tool_api

    def get_by_service_id(self, service_id: str) -> list[McpToolApi]:
        """根据服务ID获取API列表"""
        return self.db.query(McpToolApi).filter(
            McpToolApi.service_id == service_id,
            McpToolApi.is_deleted == 0
        ).all()

    def get_by_id(self, api_id: str) -> Optional[McpToolApi]:
        """根据API ID获取单个API"""
        return self.db.query(McpToolApi).filter(
            McpToolApi.id == api_id,
            McpToolApi.is_deleted == 0
        ).first()

    def delete_by_service_id(self, service_id: str) -> None:
        """删除指定服务ID的所有API记录"""
        self.db.query(McpToolApi).filter(McpToolApi.service_id == service_id).delete()
        self.db.commit()
