from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.auth import verify_token
from services.common.models.user import User
from typing import Optional
import re

class AuthMiddleware:
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 获取请求路径
            path = scope.get("path", "")
            
            # 跳过健康检查和根路径的认证
            if path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
                await self.app(scope, receive, send)
                return
                
            # 获取headers
            headers = scope.get("headers", [])
            auth_header = None
            
            # 查找Authorization header
            for key, value in headers:
                if key == b"authorization":
                    auth_header = value.decode("utf-8")
                    break
                    
            if not auth_header:
                await self._send_error_response(send, 401, "Authorization header is required")
                return
                
            # 验证Bearer token格式
            if not auth_header.startswith("Bearer "):
                await self._send_error_response(send, 401, "Invalid authorization header format")
                return
                
            token = auth_header.replace("Bearer ", "")
            
            # 验证token
            db = next(get_db())
            try:
                user = verify_token(token, db)
                if not user:
                    await self._send_error_response(send, 401, "Invalid or expired token")
                    return
                    
                # 将用户信息添加到请求状态中
                scope["user"] = user
                
            except Exception as e:
                await self._send_error_response(send, 500, "Internal server error during authentication")
                return
            finally:
                if 'db' in locals():
                    db.close()
        
        await self.app(scope, receive, send)
    
    async def _send_error_response(self, send, status_code: int, detail: str):
        # 创建错误响应
        error_response = {
            "status_code": status_code,
            "headers": [(b"content-type", b"application/json")],
            "body": f'{{"detail": "{detail}"}}'.encode("utf-8")
        }
        
        await send({
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", b"application/json")]
        })
        
        await send({
            "type": "http.response.body",
            "body": f'{{"detail": "{detail}"}}'.encode("utf-8")
        }) 