import os
import logging
from dotenv import load_dotenv

logging = logging.getLogger(__name__)

load_dotenv()


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "mysql+mysqlconnector://root:123456@172.31.126.12:3306/xpack-opensource")
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    API_PORT = int(os.getenv("API_PORT", 8002))
    ADMIN_PORT = int(os.getenv("ADMIN_PORT", 8001))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    # 基础URL，用于处理反向代理情况
    BASE_URL = os.getenv("BASE_URL", "")  # 例如: https://api.yourdomain.com
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # 数据库连接池配置
    DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", 20))  # 连接池大小
    DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", 30))  # 最大溢出连接数
    DB_POOL_TIMEOUT = int(os.getenv("DB_POOL_TIMEOUT", 30))  # 获取连接超时时间(秒)
    DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", 3600))  # 连接回收时间(秒)
    DB_POOL_PRE_PING = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"  # 连接前检测

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.example.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
    SMTP_USER = os.getenv("SMTP_USER", "your_email@example.com")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "your_password")
    SMTP_SENDER = os.getenv("SMTP_SENDER", SMTP_USER)

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "redis")
    REDIS_DB = int(os.getenv("REDIS_DB", 0))

    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
    RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "guest")
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")

    PAY_SUCCESS_URL = os.getenv("PAY_SUCCESS_URL", "http://localhost:3000/payment/pay_success")

    # 无需认证的路径配置
    # 可通过环境变量NO_AUTH_PATHS覆盖，使用逗号分隔
    _default_no_auth_paths = [
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/auth/email/send-captcha",
        "/api/auth/email/sign",
        "/api/common/config",
        "/api/auth/account/sign",
        "/api/auth/email/send_captcha",
        "/api/auth/google/sign",
        "/api/web/mcp_services",
        "/api/web/mcp_service_info",
        "/api/payment/callback_stripe",
    ]

    # 支持通过环境变量自定义无需认证的路径
    _env_no_auth_paths = os.getenv("NO_AUTH_PATHS", "")
    NO_AUTH_PATHS = (
        [path.strip() for path in _env_no_auth_paths.split(",") if path.strip()] if _env_no_auth_paths else _default_no_auth_paths
    )

    print(f"redis config loaded, host: {REDIS_HOST}, password: {REDIS_PASSWORD}")
