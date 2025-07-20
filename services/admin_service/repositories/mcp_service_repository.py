from datetime import datetime, timezone
from sqlalchemy.orm import Session
from services.common.models.mcp_service import McpService
from typing import Optional, Tuple


class McpServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def update_enabled(self, id: str, enabled: int) -> McpService:
        service = self.db.query(McpService).filter(McpService.id == id).first()
        if not service:
            raise ValueError("Service not found")
        service.enabled = enabled
        self.db.commit()
        self.db.refresh(service)
        return service

    def delete(self, id: str) -> Optional[McpService]:
        service = self.db.query(McpService).filter(McpService.id == id).first()
        if not service:
            return None
        self.db.delete(service)
        self.db.commit()
        return service

    def update(self, mcp_service: McpService) -> McpService:
        existing_service = self.db.query(McpService).filter(McpService.id == mcp_service.id).first()
        if not existing_service:
            raise ValueError("Service not found")

        existing_service.name = mcp_service.name
        existing_service.slug_name = mcp_service.slug_name
        existing_service.short_description = mcp_service.short_description
        existing_service.long_description = mcp_service.long_description
        existing_service.auth_method = mcp_service.auth_method
        existing_service.base_url = mcp_service.base_url
        existing_service.auth_header = mcp_service.auth_header
        existing_service.auth_token = mcp_service.auth_token
        existing_service.charge_type = mcp_service.charge_type
        existing_service.price = mcp_service.price

        self.db.commit()
        self.db.refresh(existing_service)
        return existing_service

    def get_by_id(self, id: str) -> Optional[McpService]:
        return self.db.query(McpService).filter(McpService.id == id).first()

    def get_by_slug_name(self, slug_name: str) -> Optional[McpService]:
        return self.db.query(McpService).filter(McpService.slug_name == slug_name).first()

    def get_all(self) -> list[McpService]:
        return self.db.query(McpService).order_by(McpService.created_at.desc()).all()

    def get_all_paginated(self, page: int = 1, page_size: int = 10) -> Tuple[list[McpService], int]:
        """Get service list with pagination"""
        # 计算偏移量
        offset = (page - 1) * page_size

        # 查询总数
        total = self.db.query(McpService).count()

        # 分页查询
        services = self.db.query(McpService).order_by(McpService.created_at.desc()).offset(offset).limit(page_size).all()

        return services, total

    def create(self, mcp_service: McpService) -> McpService:
        self.db.add(mcp_service)
        self.db.commit()
        self.db.refresh(mcp_service)
        return mcp_service

    def get_public_services_paginated(self, keyword: str, page: int = 1, page_size: int = 10) -> Tuple[list[McpService], int]:
        """Get public service list with pagination, supports keyword search"""
        # 计算偏移量
        offset = (page - 1) * page_size

        # 构建基础查询：只查询已启用的服务
        query = self.db.query(McpService).filter(McpService.enabled == 1)

        # 添加关键字搜索条件
        if keyword:
            keyword = f"%{keyword}%"
            query = query.filter((McpService.name.like(keyword)) | (McpService.short_description.like(keyword)))

        # 查询总数
        total = query.count()

        # 分页查询
        services = query.order_by(McpService.created_at.desc()).offset(offset).limit(page_size).all()

        return services, total
