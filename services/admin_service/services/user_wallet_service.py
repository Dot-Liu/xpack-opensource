from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user_wallet import UserWallet
from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.database import SessionLocal
from objtyping import to_primitive
import json
from uuid import uuid4


def get_user_wallet(db: Session, user_id: str) -> Optional[UserWallet]:
    """
    Retrieve the wallet information for a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        user_id (str): The unique identifier of the user.

    Returns:
        UserWallet or None: The UserWallet object associated with the user_id, or None if not found.
    """
    return db.query(UserWallet).filter(UserWallet.user_id == user_id).first()


def add_wallet(db: Session, user_id: str, balance: float = 0.0, frozen_balance: float = 0.0) -> Optional[UserWallet]:
    """
    新增用户钱包
    Args:
        db (Session): SQLAlchemy数据库会话
        user_id (str): 用户ID
        balance (float): 初始余额，默认0.0
        frozen_balance (float): 初始冻结余额，默认0.0
    Returns:
        UserWallet: 新建的钱包对象
    """
    wallet = UserWallet(
        id=str(uuid4()),
        user_id=user_id,
        balance=balance,
        frozen_balance=frozen_balance,
    )
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet
