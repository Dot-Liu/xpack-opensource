from sqlalchemy.orm import Session
from services.common.models.mcp_service import McpService
from typing import Optional, List


class McpServiceRepository:
    """MCP service repository layer for API service"""

    def __init__(self, db: Session):
        self.db = db

    def get_available_services(self) -> List[McpService]:
        """
        Get list of all available MCP services
        Only returns enabled services
        """
        return self.db.query(McpService).filter(McpService.enabled == 1).order_by(McpService.created_at.desc()).all()

    def get_by_id(self, service_id: str) -> Optional[McpService]:
        """
        Get single MCP service by service ID
        """
        return self.db.query(McpService).filter(McpService.id == service_id, McpService.enabled == 1).first()

    def get_by_slug_name(self, slug_name: str) -> Optional[McpService]:
        """
        Get single MCP service by slug name
        """
        return self.db.query(McpService).filter(McpService.slug_name == slug_name, McpService.enabled == 1).first()
