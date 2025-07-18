"""
MCP控制器 - 处理MCP相关的HTTP请求和SSE连接
"""
from typing import Optional
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from services.api_service.services.mcp_server_factory import McpServerFactory
from services.api_service.utils.logging_config import get_logger

logger = get_logger(__name__)


class McpController:
    """MCP控制器类"""
    
    def __init__(self):
        self.sse = SseServerTransport("/messages/")
        self.server_factory = McpServerFactory()
    
    async def handle_sse_connection(self, request: Request) -> Response:
        """
        处理SSE连接请求
        
        Args:
            request: Starlette请求对象
            
        Returns:
            Response: HTTP响应
        """
        try:
            # 从URL路径中提取service_id
            service_id = self._extract_service_id(request)
            if not service_id:
                logger.error("缺少service_id参数")
                return Response("Missing service_id parameter", status_code=400)

            logger.info(f"收到SSE连接请求 - 服务ID: {service_id}")
            
            # 创建MCP服务器实例
            mcp_server = await self.server_factory.create_server(service_id)
            
            # 建立SSE连接并运行MCP服务器
            async with self.sse.connect_sse(request.scope, request.receive, request._send) as streams:
                logger.info(f"SSE连接已建立 - 服务ID: {service_id}")
                
                # 配置服务器初始化选项
                init_options = mcp_server.create_initialization_options()
                init_options.server_name = f"mcp-service-{service_id}"
                logger.info(f"服务器名称设置为: {init_options.server_name}")
                
                # 运行MCP服务器
                await mcp_server.run(streams[0], streams[1], init_options)
                logger.info(f"MCP服务器运行结束 - 服务ID: {service_id}")
                
            return Response()
            
        except Exception as e:
            logger.error(f"SSE连接处理失败: {str(e)}", exc_info=True)
            return Response(f"Internal server error: {str(e)}", status_code=500)
    
    def _extract_service_id(self, request: Request) -> Optional[str]:
        """
        从请求中提取service_id
        
        Args:
            request: Starlette请求对象
            
        Returns:
            Optional[str]: 服务ID，如果不存在则返回None
        """
        return request.path_params.get("service_id")
    
    def get_sse_mount_handler(self):
        """获取SSE消息处理器"""
        return self.sse.handle_post_message
