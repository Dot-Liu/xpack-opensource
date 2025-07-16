import uuid
from fastapi import APIRouter, Depends, Request, Body, UploadFile, File, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.openapi_manager import openapi_manager
from services.common.utils.cache_utils import CacheUtils
from services.common.redis_keys import RedisKeys

router = APIRouter()


class OpenApiUrlRequest(BaseModel):
    """通过URL下载OpenAPI文档的请求模型"""

    url: HttpUrl
    description: Optional[str] = None


@router.post("/parse-url", response_model=dict)
async def download_openapi_from_url(request: OpenApiUrlRequest):
    try:
        # 验证URL是否可访问
        url_str = str(request.url)
        is_valid = await openapi_manager.validate_openapi_url(url_str)
        if not is_valid:
            return ResponseUtils.error(message="URL无法访问或无效", code=400)

        # 下载并解析OpenAPI文档
        openapi_for_ai = await openapi_manager.download_openapi_from_url(url_str)

        # 返回解析结果
        parse_id = str(uuid.uuid4())
        result = {"parse_id": parse_id, "openapi_info": openapi_for_ai.to_dict()}

        # 缓存解析结果
        cache_key = RedisKeys.parse_openapi_key(parse_id)
        CacheUtils.set_cache(cache_key, result, 3600)  # 缓存1小时

        return ResponseUtils.success(data=result)

    except HTTPException as e:
        return ResponseUtils.error(message=e.detail, code=e.status_code)
    except Exception as e:
        return ResponseUtils.error(message=f"处理请求时发生错误: {str(e)}", code=500)


@router.post("/parse-file", response_model=dict)
async def upload_openapi_file(file: UploadFile = File(..., description="OpenAPI文档文件（支持JSON、YAML格式）")):
    try:
        # 解析上传的文件
        openapi_for_ai = await openapi_manager.parse_openapi_from_upload(file)

        # 返回解析结果
        parse_id = str(uuid.uuid4())
        result = {"parse_id": parse_id, "openapi_info": openapi_for_ai.to_dict()}
        
        # 缓存解析结果
        cache_key = RedisKeys.parse_openapi_key(parse_id)
        CacheUtils.set_cache(cache_key, result, 3600)  # 缓存1小时

        return ResponseUtils.success(data=result, message=f"成功解析OpenAPI文档，包含 {len(openapi_for_ai.apis)} 个API端点")

    except HTTPException as e:
        return ResponseUtils.error(message=e.detail, code=e.status_code)
    except Exception as e:
        return ResponseUtils.error(message=f"处理上传文件时发生错误: {str(e)}", code=500)
