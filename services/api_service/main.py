"""
API Service - FastAPI应用主入口
专门提供MCP Streamable HTTP服务
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.routing import Route, Mount
from starlette.applications import Starlette
from contextlib import asynccontextmanager
import logging
import time

from services.common.config import Config
from services.api_service.controllers.mcp_controller import McpController
from services.api_service.utils.logging_config import setup_logging, get_logger
from services.api_service.utils.connection_manager import connection_manager

# 配置日志
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info(f"MCP Streamable HTTP Service 启动中... 端口: {Config.API_PORT}")
    
    yield
    
    logger.info("MCP Streamable HTTP Service 关闭中...")


# 创建FastAPI应用
app = FastAPI(
    title="XPack MCP Service", 
    description="XPack开源版MCP Streamable HTTP服务",
    version="1.0.0",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 添加CORS中间件 - MCP客户端需要跨域支持和重连机制
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # MCP客户端可能来自不同域名
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # 添加OPTIONS支持预检请求
    allow_headers=["*"],
    expose_headers=["*"],  # 暴露所有响应头，支持SSE重连
)

# 创建MCP控制器实例
mcp_controller = McpController()

# 健康检查端点
@app.get("/")
def read_root():
    return {
        "message": f"XPack MCP Streamable HTTP Service running on port {Config.API_PORT}",
        "version": "1.0.0",
        "protocol": "MCP Streamable HTTP",
        "endpoints": ["/mcp/sse/{service_id}", "/mcp/messages/", "/mcp/status/{service_id}"],
        "service_id_support": "Supports both service ID and slug_name",
        "reconnect_info": "Service supports automatic reconnection after restart"
    }

@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy", "service": "mcp-streamable-http"}

@app.get("/mcp/status/{service_id}")
def mcp_service_status(service_id: str):
    """
    检查指定MCP服务的状态
    MCP客户端可以使用此端点检查服务是否可用，用于重连判断
    支持service_id（UUID）和slug_name两种模式
    """
    # 解析service_id，支持ID和slug_name两种模式
    actual_service_id = None
    service_name = "unknown"
    
    try:
        from services.api_service.repositories.mcp_service_repository import McpServiceRepository
        from services.common.database import get_db
        
        db = next(get_db())
        service_repository = McpServiceRepository(db)
        
        # 首先尝试按ID查找
        service = service_repository.get_by_id(service_id)
        if service:
            actual_service_id = service.id
            service_name = service.name
        else:
            # 如果按ID未找到，尝试按slug_name查找
            service = service_repository.get_by_slug_name(service_id)
            if service:
                actual_service_id = service.id
                service_name = service.name
                
        db.close()
        
    except Exception as e:
        logger.error(f"查询服务状态时发生错误: {str(e)}")
    
    if not actual_service_id:
        return {
            "service_id": service_id,
            "status": "not_found",
            "error": "Service not found or not available"
        }
    
    # 获取该服务的连接统计
    service_connections = connection_manager.get_service_connections(actual_service_id)
    
    return {
        "service_id": actual_service_id,
        "service_identifier": service_id,
        "service_name": service_name,
        "status": "available",
        "protocol": "streamable-http",
        "endpoint": f"/mcp/sse/{service_id}",
        "message": "Service is ready for connections",
        "active_connections": len(service_connections),
        "reconnect_supported": True
    }

@app.get("/mcp/connections/stats")
def mcp_connections_stats():
    """
    获取MCP连接统计信息 - 用于监控和调试
    """
    # 清理超时连接
    connection_manager.cleanup_stale_connections()
    
    return {
        "timestamp": time.time(),
        "stats": connection_manager.get_stats()
    }

# 创建MCP Streamable HTTP路由
# 使用Starlette子应用处理MCP协议的底层SSE连接
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