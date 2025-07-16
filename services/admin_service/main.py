from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.common.config import Config
from services.admin_service.controllers import user_contoller
from services.admin_service.controllers import auth_controller
from services.admin_service.controllers import user_apikey_controller
from services.admin_service.controllers import payment_controller
from services.admin_service.controllers import order_controller
from services.admin_service.controllers import user_manager
from services.admin_service.controllers import mcp_manager
from services.admin_service.controllers import sys_config_controller
from services.admin_service.middleware import AuthMiddleware
import logging

app = FastAPI(title="Admin Service", openapi_url="/openapi.json")

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

logging.basicConfig(level=logging.DEBUG)

@app.get("/")
def read_root():
    return {"message": f"Admin Service running on port {Config.ADMIN_PORT}"}