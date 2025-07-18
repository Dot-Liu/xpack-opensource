from sqlalchemy.orm import Session
from services.common.models.mcp_service import McpService
from typing import Optional, List


class McpServiceRepository:
    """API服务的MCP服务仓储层"""

    def __init__(self, db: Session):
        self.db = db

    def get_available_services(self) -> List[McpService]:
        """
        获取所有可用的MCP服务列表
        只返回已启用的服务
        """
        return self.db.query(McpService).filter(McpService.enabled == 1).order_by(McpService.created_at.desc()).all()

    def get_by_id(self, service_id: str) -> Optional[McpService]:
        """
        根据服务ID获取单个MCP服务
        """
        return self.db.query(McpService).filter(McpService.id == service_id, McpService.enabled == 1).first()

    def get_by_slug_name(self, slug_name: str) -> Optional[McpService]:
        """
        根据slug名称获取单个MCP服务
        """
        return self.db.query(McpService).filter(McpService.slug_name == slug_name, McpService.enabled == 1).first()
