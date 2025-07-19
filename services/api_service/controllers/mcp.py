"""
MCP控制器 - 专门处理MCP Streamable HTTP协议的SSE连接和消息
支持service_id（UUID）和slug_name两种服务标识符模式
"""

from typing import Optional
from datetime import datetime, timezone
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
from services.api_service.services.mcp_server_factory import McpServerFactory
from services.common.logging_config import get_logger
from services.api_service.repositories.user_apikey_repository import UserApiKeyRepository
from services.api_service.utils.connection_manager import connection_manager
from services.common.database import get_db

logger = get_logger(__name__)


class McpController:
    """MCP Streamable HTTP控制器类 - 处理SSE连接和消息路由"""

    def __init__(self):
        self.sse = SseServerTransport("/messages/")
        self.server_factory = McpServerFactory()

    async def handle_sse_connection(self, request: Request) -> Response:
        """Handle MCP Streamable HTTP SSE connection with resume capability."""
        # 获取连接标识信息
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        service_id = None
        
        try:
            # 从URL路径中提取service_id (支持ID和slug_name两种模式)
            service_id = self._extract_service_id(request)
            if not service_id:
                logger.error("缺少service_id参数或未找到对应服务")
                return Response("Missing service_id parameter or service not found", status_code=400)

            logger.info(f"收到SSE连接请求 - 服务ID: {service_id}, 客户端: {client_ip}, UA: {user_agent[:50]}...")

            # 提取用户ID（用于计费）- 必须提供有效的 apikey
            user_id = self._extract_user_id(request)
            if not user_id:
                logger.error("缺少有效的 apikey，拒绝连接")
                return Response("Missing or invalid apikey parameter", status_code=401)

            # 创建MCP服务器实例（传入用户ID用于计费）
            mcp_server = await self.server_factory.create_server(service_id, user_id)

            # 注册连接到管理器
            connection_key = connection_manager.register_connection(service_id, user_id, client_ip)

            # 建立SSE连接并运行MCP服务器
            async with self.sse.connect_sse(request.scope, request.receive, request._send) as streams:
                logger.info(f"SSE连接已建立 - 服务ID: {service_id}, 用户ID: {user_id}, 客户端: {client_ip}")

                # 配置服务器初始化选项
                init_options = mcp_server.create_initialization_options()
                init_options.server_name = f"mcp-service-{service_id}"
                
                # 增加连接恢复提示信息
                logger.info(f"服务器名称设置为: {init_options.server_name}")
                logger.info(f"MCP服务器启动完成，等待客户端消息... (连接标识: {connection_key})")

                # 运行MCP服务器
                await mcp_server.run(streams[0], streams[1], init_options)
                logger.info(f"MCP服务器运行结束 - 服务ID: {service_id}, 用户ID: {user_id}")

            # 注销连接
            connection_manager.unregister_connection(connection_key)

            return Response()

        except ConnectionError as e:
            logger.warning(f"连接错误 - 服务ID: {service_id or 'unknown'}, 客户端: {client_ip}: {str(e)}")
            return Response("Connection error", status_code=503)
        except Exception as e:
            logger.error(f"SSE连接处理失败 - 服务ID: {service_id or 'unknown'}, 客户端: {client_ip}: {str(e)}", exc_info=True)
            return Response(f"Internal server error: {str(e)}", status_code=500)

    def _extract_service_id(self, request: Request) -> Optional[str]:
        """Extract service ID from request path, supporting both ID and slug_name."""
        service_identifier = request.path_params.get("service_id")
        if not service_identifier:
            return None
            
        # 尝试通过service_identifier查找服务，支持ID和slug_name两种模式
        db = None
        try:
            from services.api_service.repositories.mcp_service_repository import McpServiceRepository
            from services.common.database import get_db
            
            db = next(get_db())
            service_repository = McpServiceRepository(db)
            
            # 首先尝试按ID查找
            service = service_repository.get_by_id(service_identifier)
            if service:
                logger.debug(f"找到服务 (按ID): {service.name} ({service.id})")
                return service.id
            
            # 如果按ID未找到，尝试按slug_name查找
            service = service_repository.get_by_slug_name(service_identifier)
            if service:
                logger.debug(f"找到服务 (按slug_name): {service.name} ({service.id})")
                return service.id
                
            logger.warning(f"未找到服务: {service_identifier}")
            return None
            
        except Exception as e:
            logger.error(f"查询服务时发生错误: {str(e)}", exc_info=True)
            return None
        finally:
            if db is not None:
                db.close()

    def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request by validating apikey parameter."""
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
        """Get SSE message handler for processing requests."""
        return self.sse.handle_post_message
