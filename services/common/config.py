import os
import logging
from dotenv import load_dotenv

logging = logging.getLogger(__name__)

load_dotenv()


class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "mysql+mysqlconnector://root:123456@172.31.126.12:3306/xpack-opensource"
    )
    SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")
    API_PORT = int(os.getenv("API_PORT", 8000))
    ADMIN_PORT = int(os.getenv("ADMIN_PORT", 8001))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    DEBUG = os.getenv("DEBUG", "true").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
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
    
    pay_success_url = os.getenv("PAY_SUCCESS_URL", "http://localhost:3000/payment/success")
    pay_cancel_url = os.getenv("PAY_CANCEL_URL", "http://localhost:3000/payment/cancel")
    
    print("redis config loaded: %s:%d, db=%d", REDIS_HOST, REDIS_PORT, REDIS_DB)
    print("rabbitmq config loaded: %s:%d, vhost=%s", RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_VHOST)
