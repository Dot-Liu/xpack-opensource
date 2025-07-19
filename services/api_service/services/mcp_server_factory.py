"""
MCP服务器工厂 - 负责创建和配置MCP服务器实例
"""

import uuid
import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional
from mcp.server.lowlevel import Server
import mcp.types as types
from services.common.database import get_db
from services.api_service.repositories.mcp_tool_api_repository import McpToolApiRepository
from services.api_service.repositories.mcp_service_repository import McpServiceRepository
from services.api_service.services.mcp_service import McpService
from services.api_service.services.mcp_tool_service import McpToolService
from services.api_service.services.billing_service import billing_service
from services.common.models.billing import ApiCallLogInfo
from services.common.logging_config import get_logger

logger = get_logger(__name__)


class McpServerFactory:
    """MCP服务器工厂类"""

    def __init__(self):
        self.tool_service = McpToolService()
        self.billing_service = billing_service

    async def create_server(self, service_id: str, user_id: Optional[str] = None) -> Server:
        """
        为指定的service_id创建MCP服务器

        Args:
            service_id: 服务ID
            user_id: 用户ID (用于计费，可选)

        Returns:
            Server: 配置好的MCP服务器实例
        """
        logger.info(f"Creating MCP server instance - Service ID: {service_id}, User ID: {user_id}")

        app = Server(f"mcp-service-{service_id}")

        # Register tools list handler
        @app.list_tools()
        async def list_tools() -> List[types.Tool]:
            """Return available tools list for this service"""
            return await self._handle_list_tools(service_id)

        # Register tool call handler
        @app.call_tool()
        async def call_tool(name: str, arguments: dict) -> List[types.Content]:
            """Execute specified tool"""
            # user_id must exist, otherwise we shouldn't reach here
            if not user_id:
                error_msg = "Missing user authentication"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=error_msg)]
            
            return await self._handle_call_tool_with_billing(service_id, name, arguments, user_id)

        logger.info("MCP server instance created successfully")
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

    async def _handle_call_tool_with_billing(self, service_id: str, name: str, arguments: dict, user_id: str) -> List[types.Content]:
        """
        带计费逻辑的工具调用处理

        Args:
            service_id: 服务ID
            name: 工具名称
            arguments: 工具参数
            user_id: 用户ID

        Returns:
            List[types.Content]: 执行结果
        """
        call_start_time = datetime.now(timezone.utc)
        call_log_id = str(uuid.uuid4())

        logger.info(f"收到带计费的工具调用请求 - 用户ID: {user_id}, 服务ID: {service_id}, 工具名称: {name}")
        logger.debug(f"工具参数: {arguments}")

        # 1. 预扣费检查
        pre_deduct_result = await self.billing_service.check_and_pre_deduct(user_id, service_id, name)
        if not pre_deduct_result.success:
            logger.warning(f"预扣费失败: {pre_deduct_result.message}")
            error_msg = f"Billing check failed: {pre_deduct_result.message}"

            # 发送失败的计费消息
            call_log = ApiCallLogInfo(
                user_id=user_id,
                service_id=service_id,
                api_id=call_log_id,
                tool_name=name,
                input_params=json.dumps(arguments),
                unit_price=pre_deduct_result.service_price,
                call_start_time=call_start_time,
                call_end_time=datetime.now(timezone.utc),
            )
            await self.billing_service.send_billing_message(call_log, False, datetime.now(timezone.utc))

            return [types.TextContent(type="text", text=error_msg)]

        logger.info(f"预扣费成功 - 用户ID: {user_id}, 扣费金额: {pre_deduct_result.service_price}")

        # 2. 执行工具调用
        db = next(get_db())
        call_success = False
        result: List[types.ContentBlock] = []

        try:
            # 创建服务实例
            mcp_service = self._create_mcp_service(db)

            # Find tool configuration
            tool_config = mcp_service.get_tool_by_name(service_id, name)
            if not tool_config:
                error_msg = f"Unknown tool: {name}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Found tool configuration: {tool_config.name}")

            # Get service authentication info
            auth_info = mcp_service.get_service_auth_info(service_id)
            logger.debug(f"Authentication info: {auth_info}")

            # Execute tool
            result = await self.tool_service.execute_tool(tool_config, arguments, auth_info)
            call_success = True
            logger.info(f"Tool call successful - User ID: {user_id}, Tool: {name}")

        except Exception as e:
            logger.error(f"Tool call failed - User ID: {user_id}, Tool: {name}: {str(e)}", exc_info=True)
            call_success = False
            # Return error message instead of throwing exception to maintain MCP protocol stability
            error_msg = f"Tool execution failed: {str(e)}"
            result = [types.TextContent(type="text", text=error_msg)]

        finally:
            db.close()

        # 3. Send billing message
        call_end_time = datetime.now(timezone.utc)
        call_log = ApiCallLogInfo(
            user_id=user_id,
            service_id=service_id,
            api_id=call_log_id,
            tool_name=name,
            input_params=json.dumps(arguments),
            unit_price=pre_deduct_result.service_price,
            call_start_time=call_start_time,
            call_end_time=call_end_time,
        )

        await self.billing_service.send_billing_message(call_log, call_success, call_end_time)
        logger.info(f"Billing message sent - User ID: {user_id}, Tool: {name}, Success: {call_success}")

        # 确保返回类型正确
        return result

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
