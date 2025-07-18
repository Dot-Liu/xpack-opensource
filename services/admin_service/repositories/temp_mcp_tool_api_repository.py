from sqlalchemy.orm import Session
from services.common.models.temp_mcp_tool_api import TempMcpToolApi
from typing import Optional, List


class TempMcpToolApiRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, temp_mcp_tool_api: TempMcpToolApi) -> TempMcpToolApi:
        """创建临时API记录"""
        self.db.add(temp_mcp_tool_api)
        self.db.commit()
        self.db.refresh(temp_mcp_tool_api)
        return temp_mcp_tool_api

    def create_batch(self, temp_apis: List[TempMcpToolApi]) -> None:
        """批量创建临时API记录"""
        self.db.add_all(temp_apis)
        self.db.commit()

    def delete_by_service_id(self, service_id: str) -> None:
        """删除指定服务ID的所有临时API记录"""
        self.db.query(TempMcpToolApi).filter(TempMcpToolApi.service_id == service_id).delete()
        self.db.commit()

    def get_by_service_id(self, service_id: str) -> List[TempMcpToolApi]:
        """根据服务ID获取临时API列表"""
        return self.db.query(TempMcpToolApi).filter(
            TempMcpToolApi.service_id == service_id,
            TempMcpToolApi.is_deleted == 0
        ).all()

    def get_by_id(self, api_id: str) -> Optional[TempMcpToolApi]:
        """根据API ID获取单个临时API"""
        return self.db.query(TempMcpToolApi).filter(
            TempMcpToolApi.id == api_id,
            TempMcpToolApi.is_deleted == 0
        ).first()
