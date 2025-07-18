from datetime import datetime, timezone
from sqlalchemy.orm import Session
from services.common.models.temp_mcp_service import TempMcpService
from typing import Optional, List


class TempMcpServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, temp_mcp_service: TempMcpService) -> TempMcpService:
        """创建临时服务记录"""
        self.db.add(temp_mcp_service)
        self.db.commit()
        self.db.refresh(temp_mcp_service)
        return temp_mcp_service

    def delete_by_service_id(self, service_id: str) -> None:
        """删除指定服务ID的所有临时记录"""
        self.db.query(TempMcpService).filter(TempMcpService.id == service_id).delete()
        self.db.commit()

    def get_by_id(self, service_id: str) -> Optional[TempMcpService]:
        """根据服务ID获取临时服务记录"""
        return self.db.query(TempMcpService).filter(TempMcpService.id == service_id).first()

    def get_all_by_service_id(self, service_id: str) -> List[TempMcpService]:
        """获取指定服务ID的所有临时记录"""
        return self.db.query(TempMcpService).filter(TempMcpService.id == service_id).all()
