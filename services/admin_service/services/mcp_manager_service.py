import logging
import uuid
import json
import re
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from services.admin_service.repositories.mcp_service_repository import McpServiceRepository
from services.admin_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.admin_service.repositories.temp_mcp_service_repository import TempMcpServiceRepository
from services.admin_service.repositories.temp_mcp_tool_api_repository import TempMcpToolApiRepository
from services.common.models.mcp_service import McpService, AuthMethod, ChargeType
from services.common.models.mcp_tool_api import McpToolApi, HttpMethod
from services.common.models.temp_mcp_service import TempMcpService, AuthMethod as TempAuthMethod, ChargeType as TempChargeType
from services.common.models.temp_mcp_tool_api import TempMcpToolApi, HttpMethod as TempHttpMethod
from services.admin_service.services.openapi_helper import OpenApiForAI

logger = logging.getLogger(__name__)

# 工具函数：将tags字符串转换为数组
def parse_tags_to_array(tags_str: Optional[str]) -> list[str]:
    """
    将tags字符串转换为数组
    
    Args:
        tags_str: tags字符串，用半角逗号分隔
        
    Returns:
        list[str]: tags数组
    """
    if not tags_str:
        return []
    
    # 按半角逗号分割，去除空白字符
    tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
    return tags


# 工具函数：将tags数组转换为字符串
def parse_tags_to_string(tags_array: Optional[list]) -> str:
    """
    将tags数组转换为字符串
    
    Args:
        tags_array: tags数组
        
    Returns:
        str: tags字符串，用半角逗号分隔
    """
    if not tags_array or not isinstance(tags_array, list):
        return ""
    
    # 过滤空字符串，去除空白字符，用逗号连接
    tags = [str(tag).strip() for tag in tags_array if str(tag).strip()]
    return ','.join(tags)


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
        self.temp_mcp_service_repository = TempMcpServiceRepository(db)
        self.temp_mcp_tool_api_repository = TempMcpToolApiRepository(db)

    def update_enabled(self, id: str, enabled: int) -> McpService:
        return self.mcp_service_repository.update_enabled(id, enabled)

    def delete(self, id: str) -> Optional[McpService]:
        return self.mcp_service_repository.delete(id)

    def update(self, body: dict) -> bool:
        # 更新mcp_service
        service_id = body.get("id")
        if not service_id:
            raise ValueError("Service ID is required")

        # 获取更新类型，默认为 default
        update_type = body.get("update_type", "default")

        # 获取现有服务
        existing_service = self.mcp_service_repository.get_by_id(service_id)
        if not existing_service:
            raise ValueError("Service not found")

        # 如果是 openapi 类型的更新，需要先从临时表迁移数据
        if update_type == "openapi":
            # 1. 验证临时数据是否存在
            temp_service = self.temp_mcp_service_repository.get_by_id(service_id)
            if not temp_service:
                raise ValueError("No temporary data found for OpenAPI update")

            # 2. 删除现有的API数据
            self.mcp_tool_api_repository.delete_by_service_id(service_id)

            # 3. 用临时表数据更新服务信息
            existing_service.name = temp_service.name
            existing_service.short_description = temp_service.short_description
            existing_service.long_description = temp_service.long_description
            existing_service.auth_method = AuthMethod(temp_service.auth_method.value)
            existing_service.base_url = temp_service.base_url
            existing_service.auth_header = temp_service.auth_header
            existing_service.auth_token = temp_service.auth_token
            existing_service.charge_type = ChargeType(temp_service.charge_type.value)
            existing_service.price = temp_service.price
            existing_service.enabled = temp_service.enabled
            existing_service.tags = temp_service.tags

            # 4. 从临时表迁移API数据到正式表
            temp_apis = self.temp_mcp_tool_api_repository.get_by_service_id(service_id)
            for temp_api in temp_apis:
                new_api = McpToolApi()
                new_api.id = temp_api.id
                new_api.service_id = temp_api.service_id
                new_api.name = temp_api.name
                new_api.description = temp_api.description
                new_api.path = temp_api.path
                new_api.method = HttpMethod(temp_api.method.value)
                new_api.header_parameters = temp_api.header_parameters
                new_api.query_parameters = temp_api.query_parameters
                new_api.path_parameters = temp_api.path_parameters
                new_api.request_body_schema = temp_api.request_body_schema
                new_api.response_schema = temp_api.response_schema
                new_api.response_examples = temp_api.response_examples
                new_api.response_headers = temp_api.response_headers
                new_api.operation_examples = temp_api.operation_examples
                new_api.enabled = temp_api.enabled
                new_api.is_deleted = temp_api.is_deleted

                # 保存新的API记录
                self.mcp_tool_api_repository.create(new_api)

            # 5. 清理临时表数据
            self.temp_mcp_service_repository.delete_by_service_id(service_id)
            self.temp_mcp_tool_api_repository.delete_by_service_id(service_id)

        # 执行常规更新逻辑（对于两种类型都适用）
        # 只更新传入的字段
        if "name" in body and body["name"] is not None:
            existing_service.name = body["name"]
        if "slug_name" in body and body["slug_name"] is not None:
            existing_service.slug_name = body["slug_name"]
        if "short_description" in body and body["short_description"] is not None:
            existing_service.short_description = body["short_description"]
        if "long_description" in body and body["long_description"] is not None:
            existing_service.long_description = body["long_description"]
        if "auth_method" in body:
            auth_method_value = body["auth_method"]
            # 如果auth_method是None、空字符串或者"none"，就默认是free
            if auth_method_value is None or auth_method_value == "" or auth_method_value == "none":
                existing_service.auth_method = AuthMethod.FREE
            else:
                # 确保传入的值是有效的AuthMethod值
                try:
                    if isinstance(auth_method_value, str):
                        existing_service.auth_method = AuthMethod(auth_method_value.lower())
                    else:
                        existing_service.auth_method = auth_method_value
                except ValueError:
                    # 如果传入的值不是有效的AuthMethod，默认为FREE
                    existing_service.auth_method = AuthMethod.FREE
        else:
            existing_service.auth_method = AuthMethod.FREE
        if "base_url" in body and body["base_url"] is not None:
            existing_service.base_url = body["base_url"]
        if "auth_header" in body and body["auth_header"] is not None:
            existing_service.auth_header = body["auth_header"]
        if "auth_token" in body and body["auth_token"] is not None:
            existing_service.auth_token = body["auth_token"]
        if "charge_type" in body and body["charge_type"] is not None:
            charge_type_value = body["charge_type"]
            try:
                if isinstance(charge_type_value, str):
                    existing_service.charge_type = ChargeType(charge_type_value.lower())
                else:
                    existing_service.charge_type = charge_type_value
            except ValueError:
                # 如果传入的值不是有效的ChargeType，默认为FREE
                existing_service.charge_type = ChargeType.FREE
        if "price" in body and body["price"] is not None:
            existing_service.price = body["price"]
        if "tags" in body and body["tags"] is not None:
            # 如果传入的是数组，转换为字符串存储
            if isinstance(body["tags"], list):
                existing_service.tags = parse_tags_to_string(body["tags"])
            else:
                # 如果传入的是字符串，直接存储
                existing_service.tags = body["tags"]

        # 提交更改
        self.db.commit()
        self.db.refresh(existing_service)

        # 更新mcp_tool_api列表（如果提供且不是 openapi 类型更新）
        # 对于 openapi 类型，API已经在上面从临时表迁移了
        if update_type != "openapi" and "apis" in body and body["apis"] is not None:
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
            "tags": parse_tags_to_array(service.tags),
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
                tool_api.enabled = 1  # 默认开启
                tool_api.is_deleted = 0

                # 保存API
                self.mcp_tool_api_repository.create(tool_api)

            return service_id

        except Exception as e:
            logger.error(f"Failed to create service from OpenAPI: {str(e)}")
            raise ValueError(f"Failed to create service from OpenAPI: {str(e)}")

    def update_service_from_openapi(self, service_id: str, openapi_data: OpenApiForAI) -> dict:
        """
        基于OpenAPI数据更新现有服务，将更新后的数据保存到临时表

        Args:
            service_id: 要更新的服务ID
            openapi_data: 解析后的OpenAPI数据

        Returns:
            dict: 包含完整服务信息和API列表的字典

        Raises:
            ValueError: 当服务不存在或更新失败时
        """
        try:
            # 1. 检查原服务是否存在
            existing_service = self.mcp_service_repository.get_by_id(service_id)
            if not existing_service:
                raise ValueError(f"Service with ID {service_id} not found")

            # 2. 清理该服务的旧临时数据
            self.temp_mcp_service_repository.delete_by_service_id(service_id)
            self.temp_mcp_tool_api_repository.delete_by_service_id(service_id)

            # 3. 创建更新后的临时服务记录
            temp_service = TempMcpService()
            temp_service.id = service_id
            temp_service.name = openapi_data.title or existing_service.name
            temp_service.slug_name = existing_service.slug_name  # 保持原有slug_name
            temp_service.short_description = openapi_data.description or existing_service.short_description
            temp_service.long_description = openapi_data.description or existing_service.long_description
            temp_service.auth_method = TempAuthMethod(existing_service.auth_method.value)  # 保持原有认证方式
            temp_service.base_url = existing_service.base_url  # 保持原有base_url
            temp_service.auth_header = existing_service.auth_header
            temp_service.auth_token = existing_service.auth_token
            temp_service.charge_type = TempChargeType(existing_service.charge_type.value)  # 保持原有计费方式
            temp_service.price = existing_service.price  # 保持原有价格
            temp_service.enabled = existing_service.enabled  # 保持原有启用状态
            temp_service.tags = existing_service.tags  # 保持原有标签

            # 保存临时服务记录
            self.temp_mcp_service_repository.create(temp_service)

            # 4. 创建更新后的临时API记录
            temp_apis = []
            for api in openapi_data.apis:
                temp_api = TempMcpToolApi()
                temp_api.id = str(uuid.uuid4())
                temp_api.service_id = service_id
                temp_api.name = api.summary or api.path
                temp_api.description = api.description or api.summary or ""
                temp_api.path = api.path
                temp_api.method = TempHttpMethod(api.method.upper())
                temp_api.header_parameters = str(api.header_parameters) if api.header_parameters else ""
                temp_api.query_parameters = str(api.query_parameters) if api.query_parameters else ""
                temp_api.path_parameters = str(api.path_parameters) if api.path_parameters else ""
                temp_api.request_body_schema = str(api.request_body_schema) if api.request_body_schema else ""
                temp_api.response_schema = str(api.response_schema) if api.response_schema else ""
                temp_api.response_examples = str(api.response_examples) if api.response_examples else ""
                temp_api.response_headers = str(api.response_headers) if api.response_headers else ""
                temp_api.operation_examples = str(api.operation_examples) if api.operation_examples else ""
                temp_api.enabled = 0  # 默认不启用，需要管理员确认
                temp_api.is_deleted = 0

                temp_apis.append(temp_api)

            # 批量保存临时API记录
            if temp_apis:
                self.temp_mcp_tool_api_repository.create_batch(temp_apis)

            # 5. 构建返回数据
            apis_list = []
            for temp_api in temp_apis:
                api_dict = {"id": temp_api.id, "name": temp_api.name, "description": temp_api.description}
                apis_list.append(api_dict)

            result = {
                "id": temp_service.id,
                "name": temp_service.name,
                "short_description": temp_service.short_description,
                "long_description": temp_service.long_description,
                "base_url": temp_service.base_url,
                "auth_method": temp_service.auth_method.value if temp_service.auth_method else None,
                "auth_header": temp_service.auth_header,
                "auth_token": temp_service.auth_token,
                "charge_type": temp_service.charge_type.value if temp_service.charge_type else None,
                "price": str(float(temp_service.price)) if temp_service.price else "0.00",
                "enabled": temp_service.enabled,
                "tags": parse_tags_to_array(temp_service.tags),
                "apis": apis_list,
            }

            return result

        except Exception as e:
            logger.error(f"Failed to update service from OpenAPI: {str(e)}")
            raise ValueError(f"Failed to update service from OpenAPI: {str(e)}")

    def get_public_services_paginated(self, keyword: str, page: int = 1, page_size: int = 10) -> Tuple[list[dict], int]:
        """分页获取公开服务列表，返回包含API信息的格式化数据"""
        services, total = self.mcp_service_repository.get_public_services_paginated(keyword, page, page_size)

        service_list = []
        for service in services:
            # 获取服务的API列表
            apis = self.mcp_tool_api_repository.get_by_service_id(service.id)

            # 构建API信息
            api_list = []
            for api in apis:
                if api.enabled == 1:  # 只返回已启用的API
                    api_info = {"id": api.id, "name": api.name, "description": api.description}
                    api_list.append(api_info)

            # 构建服务信息
            service_info = {
                "id": service.id,
                "name": service.name,
                "short_description": service.short_description,
                "long_description": service.long_description,
                "tags": parse_tags_to_array(service.tags),
                "slug_name": service.slug_name,
                "charge_type": service.charge_type.value if service.charge_type else "free",
                "price": str(float(service.price)) if service.price else "0.00",
                "apis": api_list,
            }
            service_list.append(service_info)

        return service_list, total

    def get_public_service_info(self, id: str) -> Optional[dict]:
        """获取公开服务的详细信息（只返回已启用的服务和API）"""
        service = self.mcp_service_repository.get_by_id(id)
        if not service or service.enabled != 1:
            return None

        # 获取服务的API列表（只返回已启用的API）
        all_apis = self.mcp_tool_api_repository.get_by_service_id(id)
        apis = [api for api in all_apis if api.enabled == 1]

        # 构建API信息（按照API规范格式）
        api_list = []
        for api in apis:
            api_info = {"id": api.id, "name": api.name, "description": api.description}
            api_list.append(api_info)

        # 构建返回数据（按照API规范格式）
        service_info = {
            "id": service.id,
            "name": service.name,
            "short_description": service.short_description,
            "long_description": service.long_description,
            "slug_name": service.slug_name,
            "charge_type": service.charge_type.value if service.charge_type else "free",
            "price": f"{float(service.price):.2f}" if service.price else "0.00",
            "tags": parse_tags_to_array(service.tags),
            "apis": api_list,
        }

        return service_info
