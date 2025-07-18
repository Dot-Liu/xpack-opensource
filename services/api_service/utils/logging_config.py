"""
MCP服务日志配置
"""
import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    配置MCP服务的日志系统
    
    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        log_file: 日志文件路径，如果为None则只输出到控制台
    """
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[]
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logging.getLogger().addHandler(console_handler)
    
    # 如果指定了日志文件，添加文件处理器
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        logging.getLogger().addHandler(file_handler)
    
    # 设置第三方库的日志级别
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('starlette').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)
