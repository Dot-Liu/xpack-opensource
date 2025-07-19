from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.auth import verify_token
from services.common.models.user import User
from services.common.config import Config
from services.common.logging_config import get_logger
from services.common.utils.response_utils import ResponseUtils
from typing import Optional
import re
import json

logger = get_logger(__name__)


class AuthMiddleware:
    """
    认证中间件
    - 对所有HTTP请求进行身份验证
    - 跳过配置中定义的无需认证路径
    - 验证JWT Token并将用户信息注入到请求上下文
    """

    def __init__(self, app):
        self.app = app
        logger.info(f"AuthMiddleware initialized, no-auth paths: {len(Config.NO_AUTH_PATHS)} paths configured")

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            # 获取请求路径
            path = scope.get("path", "")

            # 跳过配置中无需认证的路径
            if path in Config.NO_AUTH_PATHS:
                logger.debug(f"Skipping authentication for path: {path}")
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
                logger.error(f"Authentication error: {str(e)}")
                await self._send_error_response(send, 500, "Internal server error during authentication")
                return
            finally:
                if "db" in locals():
                    db.close()

        await self.app(scope, receive, send)

    async def _send_error_response(self, send, status_code: int, detail: str):
        """
        使用统一的响应格式发送错误响应
        """
        # 使用 ResponseUtils 生成统一格式的错误响应
        error_response_data = ResponseUtils.error(message=detail, code=status_code)
        response_body = json.dumps(error_response_data, ensure_ascii=False).encode("utf-8")

        await send(
            {"type": "http.response.start", "status": status_code, "headers": [(b"content-type", b"application/json; charset=utf-8")]}
        )

        await send({"type": "http.response.body", "body": response_body})
