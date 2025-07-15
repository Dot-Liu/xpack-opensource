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
    return db.query(User).filter(User.user_id == user_id).first()
