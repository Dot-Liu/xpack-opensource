import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.mcp_manager_service import McpManagerService
from services.common import error_msg

logger = logging.getLogger(__name__)

router = APIRouter(tags=["front"])


def get_mcp_manager(db: Session = Depends(get_db)) -> McpManagerService:
    return McpManagerService(db)


@router.get("/mcp_services", summary="获取公开服务列表")
def get_public_mcp_services(
    keyword: Optional[str] = Query(None, description="查询字段"),
    page: Optional[int] = Query(1, description="分页，从1开始。不传就是默认1。"),
    page_size: Optional[int] = Query(10, description="分页大小，不传默认10。"),
    mcp_manager_service: McpManagerService = Depends(get_mcp_manager),
):
    """获取公开MCP服务列表，支持关键字搜索和分页"""
    try:
        # 如果没有传keyword，使用空字符串
        if keyword is None:
            keyword = ""

        # 确保分页参数合法
        if page is None or page < 1:
            page = 1
        if page_size is None or page_size < 1:
            page_size = 10

        # 获取服务列表
        service_list, total = mcp_manager_service.get_public_services_paginated(keyword=keyword, page=page, page_size=page_size)

        return ResponseUtils.success_page(data=service_list, page_num=page, page_size=page_size, total=total)

    except Exception as e:
        logger.error(f"Failed to get public MCP services: {str(e)}")
        return ResponseUtils.error(error_msg=error_msg.INTERNAL_ERROR)


@router.get("/mcp_service_info", summary="获取公开服务信息")
def get_public_mcp_service_info(
    id: str = Query(..., description="服务ID"),
    mcp_manager_service: McpManagerService = Depends(get_mcp_manager),
):
    """获取公开MCP服务的详细信息"""
    try:
        # 参数验证
        if not id:
            return ResponseUtils.error(error_msg=error_msg.PARAM_REQUIRED)
        
        # 获取服务详细信息
        service_info = mcp_manager_service.get_public_service_info(id)
        
        if not service_info:
            return ResponseUtils.error(error_msg=error_msg.NOT_FOUND)
        
        return ResponseUtils.success(data=service_info)
        
    except Exception as e:
        logger.error(f"Failed to get public MCP service info: {str(e)}")
        return ResponseUtils.error(error_msg=error_msg.INTERNAL_ERROR)
