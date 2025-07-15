from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user import User
from services.common.models.user_wallet import UserWallet
from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.database import SessionLocal
import json


def get_user(db: Session, user_id: str) -> Optional[User]:
    """
    Retrieve a user from the database by user_id.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (str): The unique identifier of the user.

    Returns:
        User: The User object if found, otherwise None.
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def add_user(db: Session, email: str, register_type: str, role_id: int = 2) -> Optional[User]:
    """
    注册新用户（用户名自动取邮箱@前部分，头像不填），并创建钱包，保证原子性事务。
    Args:
        db (Session): SQLAlchemy数据库会话
        email (str): 邮箱
        register_type (str): 注册方式（如 'email' 或 'google'）
        role_id (int): 角色ID，默认2（普通用户）
    Returns:
        User: 新建的用户对象
    """
    from uuid import uuid4
    from services.common.models.user import RegisterType
    from services.admin_service.services.user_wallet_service import add_wallet

    name = email.split("@")[0] if "@" in email else email
    try:
        user = User(
            id=str(uuid4()),
            name=name,
            email=email,
            avatar=None,
            is_active=1,
            is_deleted=0,
            register_type=RegisterType(register_type),
            role_id=role_id,
        )
        db.add(user)
        db.flush()  # 只写入但不提交，保证user.id可用
        add_wallet(db, user.id)
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise e
