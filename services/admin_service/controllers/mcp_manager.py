import uuid
import logging
from fastapi import APIRouter, Depends, Request, Body, UploadFile, File, HTTPException, Form
from pydantic import BaseModel, HttpUrl
from typing import Optional
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.openapi_manager import openapi_manager
from services.admin_service.services.mcp_manager_service import McpManagerService
from services.common.utils.cache_utils import CacheUtils
from services.common.redis_keys import RedisKeys
from services.admin_service.utils.user_utils import UserUtils
from services.common import error_msg

logger = logging.getLogger(__name__)

router = APIRouter()


class OpenApiRequest(BaseModel):
    url: Optional[HttpUrl] = None
    description: Optional[str] = None


def get_mcp_manager(db: Session = Depends(get_db)) -> McpManagerService:
    return McpManagerService(db)


@router.post("/service/enabled", summary="On/Off MCP service")
def update_mcp_service_enabled(request: Request, body: dict = Body(...), mcp_manager_service: McpManagerService = Depends(get_mcp_manager)):
    if not UserUtils.is_admin(request):
        return ResponseUtils.error(error_msg=error_msg.NO_PERMISSION)

    id = body.get("id")
    enabled = body.get("enabled")
    if id is None or enabled is None:
        return ResponseUtils.error(error_msg=error_msg.PARAM_REQUIRED)

    mcp_manager_service.update_enabled(id=id, enabled=enabled)
    return ResponseUtils.success()


@router.put("/service", summary="Update MCP service information")
def update_mcp_service_info(request: Request, body: dict = Body(...), mcp_manager_service: McpManagerService = Depends(get_mcp_manager)):
    if not UserUtils.is_admin(request):
        return ResponseUtils.error(error_msg=error_msg.NO_PERMISSION)

    mcp_manager_service.update(body)
    return ResponseUtils.success()


@router.delete("/service", summary="Delete MCP service")
def delete_mcp_service(body: dict = Body(...), mcp_manager_service: McpManagerService = Depends(get_mcp_manager)):
    id = body.get("id")
    if not id:
        return ResponseUtils.error(error_msg=error_msg.PARAM_REQUIRED)

    mcp_manager_service.delete(id)
    return ResponseUtils.success()


@router.post("/openapi_parse", summary="openapi import", response_model=dict)
async def openapi_parse(
    url: Optional[HttpUrl] = Form(None, description="OpenAPI document URL (optional)"),
    file: Optional[UploadFile] = File(None, description="OpenAPI document file (JSON/YAML, optional)"),
    mcp_manager_service: McpManagerService = Depends(get_mcp_manager),
):
    try:
        if url:
            url_str = str(url)
            is_valid = await openapi_manager.validate_openapi_url(url_str)
            if not is_valid:
                return ResponseUtils.error(error_msg=error_msg.INVALID_URL)
            openapi_for_ai = await openapi_manager.download_openapi_from_url(url_str)
        elif file:
            openapi_for_ai = await openapi_manager.parse_openapi_from_upload(file)
        else:
            return ResponseUtils.error(error_msg=error_msg.MISSING_URL_OR_FILE)

        # 创建MCP服务
        service_id = mcp_manager_service.create_service_from_openapi(openapi_for_ai)

        result = {"service_id": service_id}

        return ResponseUtils.success(data=result)
    except HTTPException as e:
        return ResponseUtils.error(message=f"Request failed: {e.detail}", code=e.status_code)
    except Exception as e:
        return ResponseUtils.error(error_msg=error_msg.INTERNAL_ERROR)


@router.get("/service/info", summary="获取MCP服务信息")
def get_mcp_service_info(request: Request, id: str, mcp_manager_service: McpManagerService = Depends(get_mcp_manager)):
    """获取单个MCP服务的详细信息，包括API列表"""
    if not UserUtils.is_admin(request):
        return ResponseUtils.error(error_msg=error_msg.NO_PERMISSION)
    
    try:
        if not id:
            return ResponseUtils.error(error_msg=error_msg.PARAM_REQUIRED)
        
        service_info = mcp_manager_service.get_service_info(id)
        if not service_info:
            return ResponseUtils.error(error_msg=error_msg.NOT_FOUND)
        
        return ResponseUtils.success(data=service_info)
    except Exception as e:
        logger.error(f"Failed to get service info: {str(e)}")
        return ResponseUtils.error(error_msg=error_msg.INTERNAL_ERROR)


@router.get("/service/list", summary="获取mcp服务列表")
def get_mcp_service_list(request: Request, page: int = 1, page_size: int = 10, mcp_manager_service: McpManagerService = Depends(get_mcp_manager)):
    """获取所有MCP服务列表（分页）"""
    if not UserUtils.is_admin(request):
        return ResponseUtils.error(error_msg=error_msg.NO_PERMISSION)
    
    try:
        # 获取分页数据
        try:
            services, total = mcp_manager_service.get_all_paginated(page=page, page_size=page_size)
        except AttributeError:
            # 如果方法不存在，使用非分页方式
            all_services = mcp_manager_service.get_all()
            total = len(all_services)
            start = (page - 1) * page_size
            end = start + page_size
            services = all_services[start:end]
        service_list = []

        for service in services:
            service_dict = {
                "id": service.id,
                "name": service.name,
                "slug_name": service.slug_name,
                "short_description": service.short_description,
                "long_description": service.long_description,
                "auth_method": service.auth_method.value if service.auth_method else None,
                "base_url": service.base_url,
                "auth_header": service.auth_header,
                "auth_token": service.auth_token,
                "charge_type": service.charge_type.value if service.charge_type else None,
                "price": float(service.price) if service.price else 0.0,
                "enabled": service.enabled,
                "created_at": str(service.created_at) if service.created_at else None,
                "updated_at": str(service.updated_at) if service.updated_at else None,
            }
            service_list.append(service_dict)

        return ResponseUtils.success_page(data=service_list, page_num=page, page_size=page_size, total=total)
    except Exception as e:
        logger.error(f"Failed to get service list: {str(e)}")
        return ResponseUtils.error(error_msg=error_msg.INTERNAL_ERROR)


# 查询所有服务列表
