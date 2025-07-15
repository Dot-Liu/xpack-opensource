from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user_wallet import UserWallet
from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.database import SessionLocal
from objtyping import to_primitive
import json


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
