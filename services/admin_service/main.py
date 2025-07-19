from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import threading
import logging
from contextlib import asynccontextmanager

from services.common.config import Config
from services.common.logging_config import setup_logging, get_logger
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
from services.admin_service.controllers import stats_data
from services.admin_service.controllers import email_test_controller
from services.admin_service.consumers.billing_message_consumer import BillingMessageConsumer
from services.admin_service.middleware import AuthMiddleware

# Setup logging for admin service
setup_logging("admin_service")
logger = get_logger(__name__)

# 全局消费者实例
consumer_instance = None
consumer_thread = None


def start_billing_consumer():
    """Start billing consumer in background thread"""
    global consumer_instance
    try:
        logger.info("Starting billing message consumer...")
        consumer_instance = BillingMessageConsumer()
        consumer_instance.start_consuming()
    except Exception as e:
        logger.error(f"Failed to start billing consumer: {str(e)}", exc_info=True)


def stop_billing_consumer():
    """停止计费消费者"""
    global consumer_instance
    if consumer_instance:
        logger.info("正在停止计费消息消费者...")
        consumer_instance.stop_consuming()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    global consumer_thread
    
    # Startup: Start consumer in separate thread
    logger.info("Admin Service starting...")
    try:
        consumer_thread = threading.Thread(target=start_billing_consumer, daemon=True)
        consumer_thread.start()
        logger.info("Billing message consumer started in background")
    except Exception as e:
        logger.error(f"Failed to start billing consumer: {str(e)}")
    
    yield
    
    # Shutdown: Stop consumer
    logger.info("Admin Service shutting down...")
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
app.include_router(stats_data.router, prefix="/api/overview")
app.include_router(email_test_controller.router, prefix="/api/email_test")

# Logging is already configured by setup_logging("admin_service")


@app.get("/")
def read_root():
    return {"message": f"Admin Service running on port {Config.ADMIN_PORT}"}
