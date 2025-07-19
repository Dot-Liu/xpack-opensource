from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import Config
from .models.base import Base
import logging

logger = logging.getLogger(__name__)

# 构建数据库引擎配置参数
engine_config = {
    "url": Config.DATABASE_URL,
    "echo": Config.DEBUG,  # 生产环境建议关闭SQL日志输出
    # 连接池配置
    "pool_size": Config.DB_POOL_SIZE,  # 连接池大小
    "max_overflow": Config.DB_MAX_OVERFLOW,  # 最大溢出连接数
    "pool_timeout": Config.DB_POOL_TIMEOUT,  # 获取连接超时时间
    "pool_recycle": Config.DB_POOL_RECYCLE,  # 连接回收时间
    "pool_pre_ping": Config.DB_POOL_PRE_PING,  # 连接前检测
    # MySQL特定配置
    "connect_args": {
        "connect_timeout": 10,  # 连接超时时间
        "read_timeout": 30,  # 读取超时时间
        "write_timeout": 30,  # 写入超时时间
        "autocommit": False,  # 禁用自动提交
        "charset": "utf8mb4",  # 字符集
        "use_unicode": True,  # 使用Unicode
    },
}

logger.info(f"数据库连接池配置: pool_size={Config.DB_POOL_SIZE}, max_overflow={Config.DB_MAX_OVERFLOW}")

engine = create_engine(**engine_config)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_pool_status():
    """
    获取数据库连接池状态信息

    Returns:
        dict: 连接池状态信息
    """
    try:
        pool = engine.pool
        # SQLAlchemy 连接池状态获取
        status = {
            "pool_size": getattr(pool, "size", lambda: Config.DB_POOL_SIZE)(),
            "checked_in_connections": getattr(pool, "checkedin", lambda: 0)(),
            "checked_out_connections": getattr(pool, "checkedout", lambda: 0)(),
            "overflow_connections": getattr(pool, "overflow", lambda: 0)(),
            "invalid_connections": getattr(pool, "invalidated", lambda: 0)(),
            "pool_config": {
                "pool_size": Config.DB_POOL_SIZE,
                "max_overflow": Config.DB_MAX_OVERFLOW,
                "pool_timeout": Config.DB_POOL_TIMEOUT,
                "pool_recycle": Config.DB_POOL_RECYCLE,
                "pool_pre_ping": Config.DB_POOL_PRE_PING,
            },
        }

        # 计算衍生指标
        checked_in = status["checked_in_connections"]
        checked_out = status["checked_out_connections"]
        status.update(
            {
                "total_connections": checked_in + checked_out,
                "available_connections": max(0, status["pool_size"] - checked_out),
                "utilization_rate": round(checked_out / max(1, status["pool_size"]) * 100, 2),
            }
        )

        return status
    except Exception as e:
        logger.error(f"获取数据库连接池状态失败: {e}")
        return {
            "error": str(e),
            "pool_config": {
                "pool_size": Config.DB_POOL_SIZE,
                "max_overflow": Config.DB_MAX_OVERFLOW,
                "pool_timeout": Config.DB_POOL_TIMEOUT,
                "pool_recycle": Config.DB_POOL_RECYCLE,
                "pool_pre_ping": Config.DB_POOL_PRE_PING,
            },
        }


def init_db():
    """初始化数据库，创建所有表"""
    try:
        # 导入所有模型以确保它们被注册
        from .models import user, user_wallet, user_wallet_history, user_access_token, sys_config, mcp_service, mcp_tool_api, user_apikey

        # 创建所有表
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功")
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        raise
