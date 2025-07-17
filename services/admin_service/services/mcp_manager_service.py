import logging
import uuid
import json
import re
from sqlalchemy.orm import Session
from typing import Optional
from services.admin_service.repositories.mcp_service_repository import McpServiceRepository
from services.admin_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.common.models.mcp_service import McpService, AuthMethod, ChargeType
from services.common.models.mcp_tool_api import McpToolApi, HttpMethod
from services.admin_service.services.openapi_helper import OpenApiForAI

logger = logging.getLogger(__name__)


def normalize_slug_name(text: str) -> str:
    """将文本转换为适合作为slug的英文字符串"""
    # 移除非英文字符，只保留字母、数字、空格、横线、下划线
    normalized = re.sub(r"[^\w\s\-]", "", text, flags=re.ASCII)
    # 将空格和横线转为下划线，转为小写
    normalized = normalized.lower().replace(" ", "_").replace("-", "_")
    # 移除多余的下划线
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    # 如果结果为空或过短，使用默认值
    if not normalized or len(normalized) < 3:
        normalized = f"service_{str(uuid.uuid4())[:8]}"
    return normalized


class McpManagerService:
    def __init__(self, db: Session):
        self.db = db
        self.mcp_service_repository = McpServiceRepository(db)
        self.mcp_tool_api_repository = McpToolApiRepository(db)

    def update_enabled(self, id: str, enabled: int) -> McpService:
        return self.mcp_service_repository.update_enabled(id, enabled)

    def delete(self, id: str) -> Optional[McpService]:
        return self.mcp_service_repository.delete(id)

    def update(self, body: dict) -> bool:
        # 更新mcp_service
        mcp_service = McpService(
            id=body.get("id"),
            name=body.get("name"),
            slug_name=body.get("slug_name"),
            short_description=body.get("short_description"),
            long_description=body.get("long_description"),
            auth_method=body.get("auth_method"),
            base_url=body.get("base_url"),
            auth_header=body.get("auth_header"),
            auth_token=body.get("auth_token"),
            charge_type=body.get("charge_type"),
            price=body.get("price"),
        )
        self.mcp_service_repository.update(mcp_service)

        # 更新mcp_tool_api列表
        for tool_api in body.get("apis", []):
            mcp_tool_api = McpToolApi(
                id=tool_api.get("id"),
                name=tool_api.get("name"),
                description=tool_api.get("description"),
            )
            self.mcp_tool_api_repository.update(mcp_tool_api)
        return True

    def get_by_id(self, id: str) -> Optional[McpService]:
        return self.mcp_service_repository.get_by_id(id)

    def get_all(self) -> list[McpService]:
        return self.mcp_service_repository.get_all()

    def create_service_from_openapi(self, openapi_data: OpenApiForAI) -> str:
        # 将OpenApiForAI信息转成 McpService对象和 McpToolApi对象列表，返回服务ID或者异常。
        try:
            # 生成服务ID
            service_id = str(uuid.uuid4())

            # 创建MCP服务
            mcp_service = McpService()
            mcp_service.id = service_id
            mcp_service.name = openapi_data.title

            # 生成唯一的slug_name
            base_slug = normalize_slug_name(openapi_data.title)
            slug_name = base_slug
            counter = 1

            while True:
                # 检查slug_name是否已存在
                try:
                    existing_service = self.mcp_service_repository.get_by_slug_name(slug_name)
                    if not existing_service:
                        break
                except AttributeError:
                    # 如果方法不存在，直接跳出循环使用当前slug_name
                    break
                # 如果存在，在后面加数字
                slug_name = f"{base_slug}-{counter}"
                counter += 1

            mcp_service.slug_name = slug_name
            mcp_service.short_description = openapi_data.description[:255] if openapi_data.description else openapi_data.title
            mcp_service.long_description = openapi_data.description
            mcp_service.auth_method = AuthMethod.FREE  # 默认免费
            mcp_service.base_url = ""  # 需要用户后续配置
            mcp_service.auth_header = ""
            mcp_service.auth_token = ""
            mcp_service.charge_type = ChargeType.FREE  # 默认免费
            mcp_service.price = 0.0
            mcp_service.enabled = 1

            # 保存服务
            self.mcp_service_repository.create(mcp_service)

            # 创建API端点
            for api in openapi_data.apis:
                tool_api = McpToolApi()
                tool_api.id = str(uuid.uuid4())
                tool_api.service_id = service_id
                tool_api.name = api.summary or f"{api.method} {api.path}"
                tool_api.description = api.description or api.summary
                tool_api.path = api.path
                tool_api.method = HttpMethod(api.method)
                tool_api.header_parameters = str(api.header_parameters) if api.header_parameters else ""
                tool_api.query_parameters = str(api.query_parameters) if api.query_parameters else ""
                tool_api.path_parameters = str(api.path_parameters) if api.path_parameters else ""
                tool_api.request_body_schema = str(api.request_body_schema) if api.request_body_schema else ""
                tool_api.response_schema = api.response_schema or {}
                tool_api.response_examples = str(api.response_examples) if api.response_examples else ""
                tool_api.response_headers = str(api.response_headers) if api.response_headers else ""
                tool_api.operation_examples = str(api.operation_examples) if api.operation_examples else ""
                tool_api.enabled = 1
                tool_api.is_deleted = 0

                # 保存API
                self.mcp_tool_api_repository.create(tool_api)

            return service_id

        except Exception as e:
            logger.error(f"Failed to create service from OpenAPI: {str(e)}")
            raise ValueError(f"Failed to create service from OpenAPI: {str(e)}")
