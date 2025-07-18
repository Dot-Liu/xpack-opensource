"""
MCP服务器主程序 - 负责启动MCP服务器和配置路由
"""

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from services.api_service.controllers.mcp_controller import McpController
from services.api_service.utils.logging_config import setup_logging, get_logger

# 配置日志
setup_logging()
logger = get_logger(__name__)


def main(port: int = 8801, transport: str = "streamable-http") -> int:
    """
    启动MCP服务器主程序

    Args:
        port: 服务器端口
        transport: 传输协议

    Returns:
        int: 退出码
    """
    logger.info(f"启动MCP服务器 - 端口: {port}, 传输协议: {transport}")

    # 创建MCP控制器
    mcp_controller = McpController()

    # 配置Starlette应用
    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse/{service_id}", endpoint=mcp_controller.handle_sse_connection, methods=["GET"]),
            Mount("/messages/", app=mcp_controller.get_sse_mount_handler()),
        ],
    )

    logger.info("Starlette应用配置完成")

    # 启动服务器
    uvicorn.run(starlette_app, host="127.0.0.1", port=port)
    return 0


if __name__ == "__main__":
    main(8801, "streamable-http")
