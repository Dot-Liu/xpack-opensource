"""
API Service - FastAPI应用主入口
整合MCP服务和HTTP API功能
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.applications import Starlette
from contextlib import asynccontextmanager
import logging

from services.common.config import Config
from services.api_service.controllers.mcp_controller import McpController
from services.api_service.utils.logging_config import setup_logging, get_logger

# 配置日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"API Service 启动中... 端口: {Config.API_PORT}")
    
    yield
    
    logger.info("API Service 关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="XPack API Service", 
    description="XPack开源版API服务，包含MCP功能",
    version="1.0.0",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # API服务通常需要支持更广泛的跨域访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建MCP控制器实例
mcp_controller = McpController()

# 健康检查端点
@app.get("/")
def read_root():
    return {
        "message": f"XPack API Service running on port {Config.API_PORT}",
        "version": "1.0.0",
        "services": ["MCP", "HTTP API"]
    }

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "api"}

# 创建Starlette子应用来处理MCP路由（因为MCP控制器使用底层Starlette API）
mcp_routes = [
    Route("/sse/{service_id}", endpoint=mcp_controller.handle_sse_connection, methods=["GET"]),
    Mount("/messages/", app=mcp_controller.get_sse_mount_handler()),
]

mcp_app = Starlette(routes=mcp_routes)

# 将MCP子应用挂载到FastAPI应用上
app.mount("/mcp", mcp_app)

# 配置日志级别
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "services.api_service.main:app",
        host="0.0.0.0",
        port=Config.API_PORT,
        reload=Config.DEBUG
    )