"""
MCP工具服务 - 负责执行MCP工具调用的业务逻辑
"""
import json
from typing import List, Dict, Any
import mcp.types as types
from mcp.shared._httpx_utils import create_mcp_http_client
from services.api_service.utils.http_client import HttpRequestBuilder
from services.api_service.utils.logging_config import get_logger

logger = get_logger(__name__)


class McpToolService:
    """MCP工具服务类"""
    
    def __init__(self):
        self.http_builder = HttpRequestBuilder()
    
    async def execute_tool(self, tool_config, arguments: dict, auth_info: dict) -> List[types.Content]:
        """
        执行工具调用
        
        Args:
            tool_config: 工具配置
            arguments: 工具参数
            auth_info: 服务认证信息
            
        Returns:
            List[types.Content]: 执行结果
        """
        try:
            logger.info(f"开始执行工具: {tool_config.name}")
            
            # 构建HTTP请求
            request_info = self.http_builder.build_request(tool_config, arguments, auth_info)
            
            # 发起HTTP请求
            response_text = await self._send_http_request(request_info)
            
            logger.info("工具执行成功完成")
            return [types.TextContent(type="text", text=response_text)]
            
        except Exception as e:
            error_msg = f"Tool execution failed: {str(e)}"
            logger.error(f"工具执行失败: {error_msg}", exc_info=True)
            return [types.TextContent(type="text", text=error_msg)]
    
    async def _send_http_request(self, request_info: Dict[str, Any]) -> str:
        """
        发送HTTP请求
        
        Args:
            request_info: 请求信息字典
            
        Returns:
            str: 响应文本
        """
        url = request_info["url"]
        method = request_info["method"]
        headers = request_info["headers"]
        query_params = request_info.get("query_params")
        request_body = request_info.get("request_body")
        
        logger.info(f"发起HTTP请求: {method} {url}")
        logger.debug(f"查询参数: {query_params}")
        logger.debug(f"请求体: {request_body}")
        
        async with create_mcp_http_client(headers=headers) as client:
            if method == "GET":
                response = await client.get(url, params=query_params)
            elif method == "POST":
                response = await client.post(url, params=query_params, json=request_body)
            elif method == "PUT":
                response = await client.put(url, params=query_params, json=request_body)
            elif method == "DELETE":
                response = await client.delete(url, params=query_params)
            elif method == "PATCH":
                response = await client.patch(url, params=query_params, json=request_body)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.info(f"HTTP响应状态码: {response.status_code}")
            response.raise_for_status()
            
            response_text = response.text
            logger.debug(f"响应内容长度: {len(response_text)} 字符")
            
            return response_text
