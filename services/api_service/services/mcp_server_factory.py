"""
MCP服务器工厂 - 负责创建和配置MCP服务器实例
"""
from typing import List
from mcp.server.lowlevel import Server
import mcp.types as types
from services.common.database import get_db
from services.api_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.api_service.repositories.mcp_service_repository import McpServiceRepository
from services.api_service.services.mcp_service import McpService
from services.api_service.services.mcp_tool_service import McpToolService
from services.api_service.utils.logging_config import get_logger

logger = get_logger(__name__)


class McpServerFactory:
    """MCP服务器工厂类"""
    
    def __init__(self):
        self.tool_service = McpToolService()
    
    async def create_server(self, service_id: str) -> Server:
        """
        为指定的service_id创建MCP服务器
        
        Args:
            service_id: 服务ID
            
        Returns:
            Server: 配置好的MCP服务器实例
        """
        logger.info(f"创建MCP服务器实例 - 服务ID: {service_id}")
        
        app = Server(f"mcp-service-{service_id}")
        
        # 注册工具列表处理器
        @app.list_tools()
        async def list_tools() -> List[types.Tool]:
            """返回该服务可用的工具列表"""
            return await self._handle_list_tools(service_id)
        
        # 注册工具调用处理器
        @app.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[types.ContentBlock]:
            """执行指定的工具"""
            return await self._handle_call_tool(service_id, name, arguments)
        
        logger.info("MCP服务器实例创建完成")
        return app
    
    async def _handle_list_tools(self, service_id: str) -> List[types.Tool]:
        """
        处理工具列表查询
        
        Args:
            service_id: 服务ID
            
        Returns:
            List[types.Tool]: 工具列表
        """
        logger.info(f"收到工具列表查询请求 - 服务ID: {service_id}")
        
        db = next(get_db())
        try:
            # 创建服务实例
            mcp_service = self._create_mcp_service(db)
            
            # 获取工具列表
            tools = mcp_service.get_tools_by_service_id(service_id)
            logger.info(f"找到 {len(tools)} 个工具")
            
            for tool in tools:
                logger.debug(f"工具: {tool.name} - {tool.description}")
            
            return tools
            
        except Exception as e:
            logger.error(f"获取工具列表失败: {str(e)}", exc_info=True)
            raise
        finally:
            db.close()
    
    async def _handle_call_tool(self, service_id: str, name: str, arguments: dict) -> List[types.ContentBlock]:
        """
        处理工具调用
        
        Args:
            service_id: 服务ID
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            List[types.ContentBlock]: 执行结果
        """
        logger.info(f"收到工具调用请求 - 服务ID: {service_id}, 工具名称: {name}")
        logger.debug(f"工具参数: {arguments}")
        
        db = next(get_db())
        try:
            # 创建服务实例
            mcp_service = self._create_mcp_service(db)
            
            # 查找工具配置
            tool_config = mcp_service.get_tool_by_name(service_id, name)
            if not tool_config:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            logger.info(f"找到工具配置: {tool_config.name}")
            
            # 获取服务认证信息
            auth_info = mcp_service.get_service_auth_info(service_id)
            logger.debug(f"认证信息: {auth_info}")
            
            # 执行工具
            return await self.tool_service.execute_tool(tool_config, arguments, auth_info)
            
        except Exception as e:
            logger.error(f"工具调用失败: {str(e)}", exc_info=True)
            # 返回错误信息而不是抛出异常，保持MCP协议的稳定性
            error_msg = f"Tool execution failed: {str(e)}"
            return [types.TextContent(type="text", text=error_msg)]
        finally:
            db.close()
    
    def _create_mcp_service(self, db) -> McpService:
        """
        创建MCP服务实例
        
        Args:
            db: 数据库连接
            
        Returns:
            McpService: MCP服务实例
        """
        tool_api_repository = McpToolApiRepository(db)
        service_repository = McpServiceRepository(db)
        return McpService(tool_api_repository, service_repository)
