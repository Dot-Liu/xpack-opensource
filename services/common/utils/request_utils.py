"""
请求相关工具函数
"""
import os
from fastapi import Request
from services.common.config import Config


class RequestUtils:
    """请求工具类"""
    
    @staticmethod
    def get_real_base_url(request: Request) -> str:
        """
        获取真实的base URL，处理反向代理的情况
        
        在反向代理环境下，直接从request获取的URL可能不是真实的外部访问地址。
        此函数按优先级检查各种来源来获取真实的base URL：
        
        1. X-Forwarded-Proto + X-Forwarded-Host 头部
        2. X-Forwarded-Proto + Host 头部  
        3. 标准的 Forwarded 头部 (RFC 7239)
        4. 配置文件中的 BASE_URL
        5. 直接从request获取（fallback）
        
        Args:
            request: FastAPI Request对象
            
        Returns:
            str: 真实的base URL，格式如 https://api.yourdomain.com
            
        Examples:
            >>> # 在nginx反向代理后面
            >>> # nginx配置: proxy_set_header X-Forwarded-Proto $scheme;
            >>> # nginx配置: proxy_set_header X-Forwarded-Host $host;
            >>> base_url = RequestUtils.get_real_base_url(request)
            >>> # 返回: https://api.yourdomain.com
        """
        # 1. 优先检查反向代理头部信息
        forwarded_proto = request.headers.get("X-Forwarded-Proto") or request.headers.get("X-Forwarded-Protocol")
        forwarded_host = request.headers.get("X-Forwarded-Host") or request.headers.get("X-Forwarded-Server")
        
        if forwarded_proto and forwarded_host:
            return f"{forwarded_proto}://{forwarded_host}"
        
        # 2. 检查其他常见的代理头部
        if forwarded_proto and request.headers.get("Host"):
            return f"{forwarded_proto}://{request.headers.get('Host')}"
        
        # 3. 检查 Forwarded 标准头部 (RFC 7239)
        forwarded = request.headers.get("Forwarded")
        if forwarded:
            # 解析 Forwarded 头部，格式如: for=192.0.2.60;proto=http;by=203.0.113.43;host=example.com
            parts = {}
            for part in forwarded.split(';'):
                if '=' in part:
                    key, value = part.strip().split('=', 1)
                    parts[key] = value.strip('"')
            
            if 'proto' in parts and 'host' in parts:
                return f"{parts['proto']}://{parts['host']}"
        
        # 4. 从配置中获取（如果有配置的话）
        if Config.BASE_URL:
            return Config.BASE_URL.rstrip('/')
        
        # 5. 最后fallback到直接从request获取
        return f"{request.url.scheme}://{request.url.netloc}"
    
    @staticmethod 
    def get_client_ip(request: Request) -> str:
        """
        获取客户端真实IP地址，处理反向代理的情况
        
        Args:
            request: FastAPI Request对象
            
        Returns:
            str: 客户端真实IP地址
        """
        # 检查常见的代理头部
        for header in ["X-Forwarded-For", "X-Real-IP", "X-Client-IP"]:
            ip = request.headers.get(header)
            if ip:
                # X-Forwarded-For 可能包含多个IP，取第一个
                return ip.split(',')[0].strip()
        
        # 检查 Forwarded 标准头部
        forwarded = request.headers.get("Forwarded")
        if forwarded:
            for part in forwarded.split(';'):
                if part.strip().startswith('for='):
                    ip = part.strip().split('=', 1)[1].strip('"')
                    # 移除端口号
                    if ':' in ip and not ip.startswith('['):
                        ip = ip.split(':')[0]
                    elif ip.startswith('[') and ']:' in ip:
                        ip = ip.split(']:')[0] + ']'
                    return ip
        
        # fallback到直接获取
        return request.client.host if request.client else "unknown"
