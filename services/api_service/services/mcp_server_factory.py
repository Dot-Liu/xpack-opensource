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
from services.api_service.utils.logging_config import get_logger

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
        logger.info(f"创建MCP服务器实例 - 服务ID: {service_id}, 用户ID: {user_id}")

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
            # user_id 必须存在，否则不应该到达这里
            if not user_id:
                error_msg = "Missing user authentication"
                logger.error(error_msg)
                return [types.TextContent(type="text", text=error_msg)]
            
            return await self._handle_call_tool_with_billing(service_id, name, arguments, user_id)

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

    async def _handle_call_tool_with_billing(self, service_id: str, name: str, arguments: dict, user_id: str) -> List[types.ContentBlock]:
        """
        带计费逻辑的工具调用处理

        Args:
            service_id: 服务ID
            name: 工具名称
            arguments: 工具参数
            user_id: 用户ID

        Returns:
            List[types.ContentBlock]: 执行结果
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
            result = await self.tool_service.execute_tool(tool_config, arguments, auth_info)
            call_success = True
            logger.info(f"工具调用成功 - 用户ID: {user_id}, 工具: {name}")

        except Exception as e:
            logger.error(f"工具调用失败 - 用户ID: {user_id}, 工具: {name}: {str(e)}", exc_info=True)
            call_success = False
            # 返回错误信息而不是抛出异常，保持MCP协议的稳定性
            error_msg = f"Tool execution failed: {str(e)}"
            result = [types.TextContent(type="text", text=error_msg)]

        finally:
            db.close()

        # 3. 发送计费消息
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
        logger.info(f"计费消息已发送 - 用户ID: {user_id}, 工具: {name}, 成功: {call_success}")

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
