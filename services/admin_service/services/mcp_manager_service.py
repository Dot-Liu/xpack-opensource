import logging
import uuid
import json
import re
from sqlalchemy.orm import Session
from typing import Optional, Tuple
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
        service_id = body.get("id")
        if not service_id:
            raise ValueError("Service ID is required")

        # 获取现有服务
        existing_service = self.mcp_service_repository.get_by_id(service_id)
        if not existing_service:
            raise ValueError("Service not found")

        # 只更新传入的字段
        if "name" in body and body["name"] is not None:
            existing_service.name = body["name"]
        if "slug_name" in body and body["slug_name"] is not None:
            existing_service.slug_name = body["slug_name"]
        if "short_description" in body and body["short_description"] is not None:
            existing_service.short_description = body["short_description"]
        if "long_description" in body and body["long_description"] is not None:
            existing_service.long_description = body["long_description"]
        if "auth_method" in body and body["auth_method"] is not None:
            existing_service.auth_method = body["auth_method"]
        if "base_url" in body and body["base_url"] is not None:
            existing_service.base_url = body["base_url"]
        if "auth_header" in body and body["auth_header"] is not None:
            existing_service.auth_header = body["auth_header"]
        if "auth_token" in body and body["auth_token"] is not None:
            existing_service.auth_token = body["auth_token"]
        if "charge_type" in body and body["charge_type"] is not None:
            existing_service.charge_type = body["charge_type"]
        if "price" in body and body["price"] is not None:
            existing_service.price = body["price"]
        if "tags" in body and body["tags"] is not None:
            existing_service.tags = body["tags"]

        # 提交更改
        self.db.commit()
        self.db.refresh(existing_service)

        # 更新mcp_tool_api列表（如果提供）
        if "apis" in body and body["apis"] is not None:
            for tool_api_data in body["apis"]:
                api_id = tool_api_data.get("id")
                if not api_id:
                    continue

                existing_api = self.mcp_tool_api_repository.get_by_id(api_id)
                if not existing_api:
                    continue

                # 只更新传入的API字段
                if "name" in tool_api_data and tool_api_data["name"] is not None:
                    existing_api.name = tool_api_data["name"]
                if "description" in tool_api_data and tool_api_data["description"] is not None:
                    existing_api.description = tool_api_data["description"]
                if "path" in tool_api_data and tool_api_data["path"] is not None:
                    existing_api.path = tool_api_data["path"]
                if "method" in tool_api_data and tool_api_data["method"] is not None:
                    existing_api.method = tool_api_data["method"]
                if "header_parameters" in tool_api_data and tool_api_data["header_parameters"] is not None:
                    existing_api.header_parameters = tool_api_data["header_parameters"]
                if "query_parameters" in tool_api_data and tool_api_data["query_parameters"] is not None:
                    existing_api.query_parameters = tool_api_data["query_parameters"]
                if "path_parameters" in tool_api_data and tool_api_data["path_parameters"] is not None:
                    existing_api.path_parameters = tool_api_data["path_parameters"]
                if "request_body_schema" in tool_api_data and tool_api_data["request_body_schema"] is not None:
                    existing_api.request_body_schema = tool_api_data["request_body_schema"]
                if "response_schema" in tool_api_data and tool_api_data["response_schema"] is not None:
                    # 如果传入的是字典，转换为JSON字符串
                    if isinstance(tool_api_data["response_schema"], dict):
                        existing_api.response_schema = json.dumps(tool_api_data["response_schema"])
                    else:
                        existing_api.response_schema = str(tool_api_data["response_schema"])
                if "response_examples" in tool_api_data and tool_api_data["response_examples"] is not None:
                    existing_api.response_examples = tool_api_data["response_examples"]
                if "response_headers" in tool_api_data and tool_api_data["response_headers"] is not None:
                    existing_api.response_headers = tool_api_data["response_headers"]
                if "operation_examples" in tool_api_data and tool_api_data["operation_examples"] is not None:
                    existing_api.operation_examples = tool_api_data["operation_examples"]
                if "enabled" in tool_api_data and tool_api_data["enabled"] is not None:
                    existing_api.enabled = tool_api_data["enabled"]

                # 提交API更改
                self.db.commit()
                self.db.refresh(existing_api)

        return True

    def get_by_id(self, id: str) -> Optional[McpService]:
        return self.mcp_service_repository.get_by_id(id)

    def get_service_info(self, id: str) -> Optional[dict]:
        """获取服务详细信息，包括API列表"""
        service = self.mcp_service_repository.get_by_id(id)
        if not service:
            return None

        # 获取服务的API列表
        apis = self.mcp_tool_api_repository.get_by_service_id(id)

        # 构建返回数据
        service_info = {
            "id": service.id,
            "name": service.name,
            "short_description": service.short_description,
            "long_description": service.long_description,
            "base_url": service.base_url,
            "auth_method": service.auth_method.value if service.auth_method else None,
            "auth_header": service.auth_header,
            "auth_token": service.auth_token,
            "charge_type": service.charge_type.value if service.charge_type else None,
            "price": str(float(service.price)) if service.price else "0.00",
            "enabled": service.enabled,
            "tags": service.tags,
            "apis": [{"id": api.id, "name": api.name, "description": api.description} for api in apis],
        }

        return service_info

    def get_all(self) -> list[McpService]:
        return self.mcp_service_repository.get_all()

    def get_all_paginated(self, page: int = 1, page_size: int = 10) -> Tuple[list[McpService], int]:
        """分页获取服务列表"""
        return self.mcp_service_repository.get_all_paginated(page=page, page_size=page_size)

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
            mcp_service.enabled = 0  # 默认不开启，需要用户手动开启

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
                tool_api.response_schema = json.dumps(api.response_schema) if api.response_schema else ""
                tool_api.response_examples = str(api.response_examples) if api.response_examples else ""
                tool_api.response_headers = str(api.response_headers) if api.response_headers else ""
                tool_api.operation_examples = str(api.operation_examples) if api.operation_examples else ""
                tool_api.enabled = 0  # 默认不开启，需要用户手动开启
                tool_api.is_deleted = 0

                # 保存API
                self.mcp_tool_api_repository.create(tool_api)

            return service_id

        except Exception as e:
            logger.error(f"Failed to create service from OpenAPI: {str(e)}")
            raise ValueError(f"Failed to create service from OpenAPI: {str(e)}")
