import json
import mcp.types as types
from typing import List, Optional
from services.common.models.mcp_tool_api import McpToolApi
from services.common.models.mcp_service import McpService as McpServiceModel
from services.api_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.api_service.repositories.mcp_service_repository import McpServiceRepository


class McpService:
    """MCP服务业务逻辑层"""

    def __init__(self, tool_api_repository: McpToolApiRepository, service_repository: McpServiceRepository):
        self.tool_api_repository = tool_api_repository
        self.service_repository = service_repository

    def get_tools_by_service_id(self, service_id: str) -> List[types.Tool]:
        """
        根据服务ID获取该服务的所有工具列表
        
        Args:
            service_id: 服务ID
            
        Returns:
            List[types.Tool]: MCP工具列表
        """
        # 从数据库获取工具配置
        tool_apis = self.tool_api_repository.get_by_service_id(service_id)
        
        # 转换为MCP工具格式
        tools = []
        for tool_api in tool_apis:
            tool = self._convert_api_to_tool(tool_api)
            if tool:
                tools.append(tool)
        
        return tools

    def _convert_api_to_tool(self, tool_api: McpToolApi) -> Optional[types.Tool]:
        """
        将数据库中的API配置转换为MCP工具
        
        Args:
            tool_api: 数据库中的API配置
            
        Returns:
            Optional[types.Tool]: 转换后的MCP工具，转换失败时返回None
        """
        try:
            # 构建输入schema
            input_schema = self._build_input_schema(tool_api)
            
            return types.Tool(
                name=tool_api.name,
                title=tool_api.name.replace('_', ' ').title(),
                description=tool_api.description,
                inputSchema=input_schema
            )
        except Exception as e:
            print(f"转换工具失败 {tool_api.name}: {e}")
            return None

    def _build_input_schema(self, tool_api: McpToolApi) -> dict:
        """
        根据API配置构建输入schema
        
        Args:
            tool_api: API配置
            
        Returns:
            dict: JSON Schema格式的输入定义
        """
        schema = {
            "type": "object",
            "properties": {},
            "required": []
        }
        
        # 解析路径参数
        if tool_api.path_parameters:
            try:
                path_params = json.loads(tool_api.path_parameters)
                for param in path_params:
                    if isinstance(param, dict) and "name" in param:
                        schema["properties"][param["name"]] = {
                            "type": param.get("type", "string"),
                            "description": param.get("description", f"Path parameter: {param['name']}")
                        }
                        if param.get("required", False):
                            schema["required"].append(param["name"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 解析查询参数
        if tool_api.query_parameters:
            try:
                query_params = json.loads(tool_api.query_parameters)
                for param in query_params:
                    if isinstance(param, dict) and "name" in param:
                        schema["properties"][param["name"]] = {
                            "type": param.get("type", "string"),
                            "description": param.get("description", f"Query parameter: {param['name']}")
                        }
                        if param.get("required", False):
                            schema["required"].append(param["name"])
            except (json.JSONDecodeError, TypeError):
                pass
        
        # 解析请求体参数
        if tool_api.request_body_schema:
            try:
                body_schema = json.loads(tool_api.request_body_schema)
                if isinstance(body_schema, dict) and "properties" in body_schema:
                    schema["properties"].update(body_schema["properties"])
                    if "required" in body_schema:
                        schema["required"].extend(body_schema["required"])
            except (json.JSONDecodeError, TypeError):
                pass
        return schema

    def get_tool_by_name(self, service_id: str, tool_name: str) -> Optional[McpToolApi]:
        """
        根据服务ID和工具名称获取工具配置
        
        Args:
            service_id: 服务ID
            tool_name: 工具名称
            
        Returns:
            Optional[McpToolApi]: 工具配置，未找到时返回None
        """
        tool_apis = self.tool_api_repository.get_by_service_id(service_id)
        for tool_api in tool_apis:
            if tool_api.name == tool_name:
                return tool_api
        return None

    def get_service_by_id(self, service_id: str) -> Optional[McpServiceModel]:
        """
        根据服务ID获取服务信息
        
        Args:
            service_id: 服务ID
            
        Returns:
            Optional[McpServiceModel]: 服务信息，未找到时返回None
        """
        return self.service_repository.get_by_id(service_id)

    def get_service_auth_info(self, service_id: str) -> dict:
        """
        获取服务的认证信息
        
        Args:
            service_id: 服务ID
            
        Returns:
            dict: 包含base_url和认证信息的字典
        """
        service = self.service_repository.get_by_id(service_id)
        if not service:
            return {}
        
        auth_info = {
            "base_url": service.base_url or "",
            "auth_method": service.auth_method.value if service.auth_method else "free",
            "auth_header": service.auth_header or "",
            "auth_token": service.auth_token or ""
        }
        
        return auth_info
