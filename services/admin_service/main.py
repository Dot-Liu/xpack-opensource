from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading
import logging
from contextlib import asynccontextmanager

from services.common.config import Config
from services.admin_service.controllers import user_contoller
from services.admin_service.controllers import auth_controller
from services.admin_service.controllers import user_apikey_controller
from services.admin_service.controllers import payment_controller
from services.admin_service.controllers import order_controller
from services.admin_service.controllers import user_manager
from services.admin_service.controllers import mcp_manager
from services.admin_service.controllers import sys_config_controller
from services.admin_service.controllers import payment_channel_controller
from services.admin_service.controllers import init_config
from services.admin_service.controllers import web_controller
from services.admin_service.consumers.billing_message_consumer import BillingMessageConsumer
from services.admin_service.middleware import AuthMiddleware

logger = logging.getLogger(__name__)

# 全局消费者实例
consumer_instance = None
consumer_thread = None


def start_billing_consumer():
    """在后台线程中启动计费消费者"""
    global consumer_instance
    try:
        logger.info("正在启动计费消息消费者...")
        consumer_instance = BillingMessageConsumer()
        consumer_instance.start_consuming()
    except Exception as e:
        logger.error(f"计费消费者启动失败: {str(e)}", exc_info=True)


def stop_billing_consumer():
    """停止计费消费者"""
    global consumer_instance
    if consumer_instance:
        logger.info("正在停止计费消息消费者...")
        consumer_instance.stop_consuming()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global consumer_thread
    
    # 启动时：在单独线程中启动消费者
    logger.info("Admin Service 启动中...")
    try:
        consumer_thread = threading.Thread(target=start_billing_consumer, daemon=True)
        consumer_thread.start()
        logger.info("计费消息消费者已在后台启动")
    except Exception as e:
        logger.error(f"启动计费消费者失败: {str(e)}")
    
    yield
    
    # 关闭时：停止消费者
    logger.info("Admin Service 关闭中...")
    stop_billing_consumer()


app = FastAPI(title="Admin Service", openapi_url="/openapi.json", lifespan=lifespan)

# 添加认证中间件
app.add_middleware(AuthMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[Config.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_contoller.router, prefix="/api/user")
app.include_router(auth_controller.router, prefix="/api/auth")
app.include_router(user_apikey_controller.router, prefix="/api/apikey")
app.include_router(user_manager.router, prefix="/api/user_manager")
app.include_router(payment_controller.router, prefix="/api/payment")
app.include_router(mcp_manager.router, prefix="/api/mcp")
app.include_router(order_controller.router, prefix="/api/order")
app.include_router(sys_config_controller.router, prefix="/api/sysconfig")
app.include_router(payment_channel_controller.router, prefix="/api/payment_channel")
app.include_router(init_config.router, prefix="/api/common")
app.include_router(web_controller.router, prefix="/api/web")

logging.basicConfig(level=logging.DEBUG)


@app.get("/")
def read_root():
    return {"message": f"Admin Service running on port {Config.ADMIN_PORT}"}
