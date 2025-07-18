from sqlalchemy.orm import Session
from services.common.models.mcp_tool_api import McpToolApi
from typing import Optional, List


class McpToolApiRepository:
    """API服务的MCP工具API仓储层"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_service_id(self, service_id: str) -> List[McpToolApi]:
        """
        根据服务ID获取该服务下的所有API列表
        只返回已启用且未删除的API
        """
        return (
            self.db.query(McpToolApi).filter(McpToolApi.service_id == service_id, McpToolApi.enabled == 1, McpToolApi.is_deleted == 0).all()
        )

    def get_by_id(self, api_id: str) -> Optional[McpToolApi]:
        """
        根据API ID获取单个API
        只返回已启用且未删除的API
        """
        return self.db.query(McpToolApi).filter(McpToolApi.id == api_id, McpToolApi.enabled == 1, McpToolApi.is_deleted == 0).first()
