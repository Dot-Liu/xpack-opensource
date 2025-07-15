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
from services.admin_service.services import user_service
import json
from datetime import datetime, timedelta, timezone
import uuid

logger = logging.getLogger(__name__)


def send_email_login_captcha(email: str) -> bool:
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


def email_login(db: Session, email: str, captcha: str) -> Optional[str]:
    cache_value = CacheUtils.get_cache(RedisKeys.email_login_captcha(email))
    if cache_value is None:
        logger.warning(f"not found captcha, email: {email}")
        return None
    if captcha == cache_value:
        logging.info(f"check email login code right, email: {email}")
        user = user_service.get_user_by_email(db, email)

        # 用户不存在，先注册
        if user is None:
            user = user_service.add_user(db, email=email, register_type="email", role_id=2)
        if user is None:
            logger.warning(f"Failed to register user with email: {email}")
            return None

        # 创建用户访问令牌
        token = create_user_token(db, user.id)
        if token is None:
            logger.warning(f"Failed to create user token for email: {email}")
            return None
        # 清除验证码缓存
        CacheUtils.set_cache(RedisKeys.email_login_captcha(email), None)
        return token
    return None


def create_user_token(db: Session, user_id: str) -> Optional[str]:
    id = str(uuid.uuid4())
    token = str(uuid.uuid4())
    expire_at = datetime.now(timezone.utc) + timedelta(days=30)
    user_access_token = UserAccessToken(id=id, user_id=user_id, token=token, expire_at=expire_at)
    db.add(user_access_token)
    db.commit()
    return token
