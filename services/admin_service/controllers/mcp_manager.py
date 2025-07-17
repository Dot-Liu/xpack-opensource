import uuid
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
