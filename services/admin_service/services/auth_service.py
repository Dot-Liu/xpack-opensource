import random
import logging
from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user import User
from services.common.models.user_wallet import UserWallet
from services.common.models.user_access_token import UserAccessToken

from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.database import SessionLocal
from services.common.utils.email_utils import EmailUtils
from services.common.utils.cache_utils import CacheUtils
from services.common.redis_keys import RedisKeys
from services.common.config import Config

from services.admin_service.repositories.user_repository import UserRepository
from services.admin_service.repositories.user_access_token_repository import UserAccessTokenRepository

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import id_token
import requests

logger = logging.getLogger(__name__)


class AuthService:

    def __init__(self, db: Session = SessionLocal()):
        self.user_repository = UserRepository(db)
        self.user_access_token_repository = UserAccessTokenRepository(db)

    def send_email_login_captcha(self, email: str) -> bool:
        """
        Sends a login captcha code to the specified email address.
        The function generates a random 4-digit captcha code, stores it in Redis cache for 10 minutes,
        and sends the code to the user's email. Returns the captcha code if the email was sent successfully,
        otherwise returns None.
        Args:
            email (str): The recipient's email address.
        Returns:
            Optional[str]: The captcha code if email was sent successfully, otherwise None.
        """
        # 快速生成随机四位整数。
        captcha = str(random.randint(1000, 9999))

        # 缓存到 redis
        CacheUtils.set_cache(RedisKeys.email_login_captcha(email), captcha, 10 * 60)

        # 发送邮件
        return EmailUtils.send_email("XPack code", f"code: {captcha}", email, False)

    def email_login(self, email: str, captcha: str) -> Optional[str]:
        cache_value = CacheUtils.get_cache(RedisKeys.email_login_captcha(email))
        if cache_value is None:
            logger.warning(f"not found captcha, email: {email}")
            return None
        if captcha == cache_value:
            logger.info(f"check email login code right, email: {email}")
            user = self.user_repository.get_by_email(email)

            # 用户不存在，先注册
            if user is None:
                user = self.user_repository.create(email=email, register_type="email", role_id=2)
            if user is None:
                logger.warning(f"Failed to register user with email: {email}")
                return None

            # 创建用户访问令牌
            token = self.create_user_token(user.id)
            if token is None:
                logger.warning(f"Failed to create user token for email: {email}")
                return None
            # 清除验证码缓存
            CacheUtils.set_cache(RedisKeys.email_login_captcha(email), None)
            return token
        return None

    def create_user_token(self, user_id: str) -> Optional[str]:
        user_access_token = self.user_access_token_repository.create(user_id)
        if user_access_token is None:
            logger.error(f"Failed to create user access token for user_id: {user_id}")
            return None
        # 缓存用户访问令牌
        return user_access_token.token

    def account_login(self, account: str, password: str) -> Optional[str]:
        user = self.user_repository.get_by_account(account)
        if user and user.password == password:
            token = self.create_user_token(user.id)
            if token:
                return token
        return None

    def logout(self, token: str) -> bool:
        """
        Logs out the user by deleting their access token.
        Args:
            token (str): The user's access token.
        Returns:
            bool: True if logout was successful, False otherwise.
        """
        try:
            self.user_access_token_repository.delete_by_token(token)
            return True
        except Exception as e:
            logger.error(f"Failed to logout user with token {token}: {e}")
            return False

    def google_login(self, code: str, state: str) -> Optional[str]:
        """
        Google OAuth login method.
        Args:
            code (str): Google OAuth authorization code
            state (str): OAuth state parameter for security
        Returns:
            Optional[str]: User token if login successful, None otherwise
        """
        try:
            # Exchange authorization code for access token
            token_url = "https://oauth2.googleapis.com/token"
            token_data = {
                "client_id": Config.GOOGLE_CLIENT_ID,
                "client_secret": Config.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": Config.GOOGLE_REDIRECT_URI,
            }

            token_response = requests.post(token_url, data=token_data)
            if token_response.status_code != 200:
                logger.error(f"Failed to exchange code for token: {token_response.text}")
                return None

            token_json = token_response.json()
            id_token_str = token_json.get("id_token")

            if not id_token_str:
                logger.error("No id_token in Google OAuth response")
                return None

            # Verify and decode the ID token
            try:
                idinfo = id_token.verify_oauth2_token(id_token_str, GoogleRequest(), Config.GOOGLE_CLIENT_ID)
            except ValueError as e:
                logger.error(f"Invalid Google ID token: {e}")
                return None

            # Extract user information
            email = idinfo.get("email")
            name = idinfo.get("name")
            google_id = idinfo.get("sub")

            if not email:
                logger.error("No email in Google user info")
                return None

            # Check if user already exists
            user = self.user_repository.get_by_email(email)

            # Create user if doesn't exist
            if user is None:
                user = self.user_repository.create_google_user(email=email, name=name or email.split("@")[0], google_id=google_id)

            if user is None:
                logger.error(f"Failed to create/get user with email: {email}")
                return None

            # Create user token
            token = self.create_user_token(user.id)
            if token is None:
                logger.error(f"Failed to create user token for email: {email}")
                return None

            logger.info(f"Google login successful for email: {email}")
            return token

        except Exception as e:
            logger.error(f"Google login failed: {e}")
            return None
