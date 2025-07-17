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
