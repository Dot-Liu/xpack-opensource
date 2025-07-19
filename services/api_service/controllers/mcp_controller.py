"""
MCP控制器 - 处理MCP相关的HTTP请求和SSE连接
"""

from typing import Optional
from datetime import datetime, timezone
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from services.api_service.services.mcp_server_factory import McpServerFactory
from services.api_service.utils.logging_config import get_logger
from services.api_service.repositories.user_apikey_repository import UserApiKeyRepository
from services.common.database import get_db

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

            # 提取用户ID（用于计费）- 必须提供有效的 apikey
            user_id = self._extract_user_id(request)
            if not user_id:
                logger.error("缺少有效的 apikey，拒绝连接")
                return Response("Missing or invalid apikey parameter", status_code=401)

            # 创建MCP服务器实例（传入用户ID用于计费）
            mcp_server = await self.server_factory.create_server(service_id, user_id)

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

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """
        从请求中提取user_id（用于计费）
        通过URL参数中的apikey查询user_apikey表获取用户ID

        Args:
            request: Starlette请求对象

        Returns:
            Optional[str]: 用户ID，如果不存在则返回None
        """
        # 从URL查询参数中获取apikey
        apikey = request.query_params.get("apikey")
        if not apikey:
            logger.warning("未在URL参数中找到apikey")
            return None

        logger.debug(f"正在验证apikey: {apikey[:10]}...")  # 只记录前10个字符用于调试

        db = None
        try:
            # 创建数据库会话
            db = next(get_db())
            user_apikey_repo = UserApiKeyRepository(db)
            
            # 通过apikey查询用户信息
            user_apikey = user_apikey_repo.get_by_apikey(apikey)
            if not user_apikey:
                logger.warning(f"数据库中未找到apikey: {apikey[:10]}...")
                return None
            
            logger.debug(f"找到apikey记录 - 用户ID: {user_apikey.user_id}, 过期时间: {user_apikey.expire_at}")
            
            # 检查apikey是否过期
            if user_apikey.expire_at:
                # 确保时区一致性
                if user_apikey.expire_at.tzinfo is None:
                    expire_at_utc = user_apikey.expire_at.replace(tzinfo=timezone.utc)
                else:
                    expire_at_utc = user_apikey.expire_at
                    
                if expire_at_utc < datetime.now(timezone.utc):
                    logger.warning(f"apikey已过期: {apikey[:10]}..., 过期时间: {user_apikey.expire_at}")
                    return None
            
            logger.info(f"apikey验证成功 - 用户ID: {user_apikey.user_id}")
            return user_apikey.user_id
            
        except Exception as e:
            logger.error(f"查询用户apikey时发生错误: {str(e)}", exc_info=True)
            return None
        finally:
            if db is not None:
                db.close()

    def get_sse_mount_handler(self):
        """获取SSE消息处理器"""
        return self.sse.handle_post_message
