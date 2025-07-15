from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user_apikey import UserApiKey
from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.database import SessionLocal
from datetime import datetime, timedelta, timezone
import json


def add_apikey(db: Session, user_id: str, name: str) -> Optional[UserApiKey]:
    """
    Create a new API key for the user.
    Args:
        db (Session): SQLAlchemy session
        user_id (str): User ID
        name (str): API key name
    Returns:
        UserApiKey: The created API key object
    """
    from uuid import uuid4
    from datetime import datetime
    import secrets

    apikey = secrets.token_urlsafe(32)
    try:
        user_apikey = UserApiKey(
            id=str(uuid4()),
            user_id=user_id,
            name=name,
            apikey=apikey,
            expire_at=datetime.now(timezone.utc) + timedelta(days=365),  # 默认一年有效期
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(user_apikey)
        db.commit()
        db.refresh(user_apikey)
        return user_apikey
    except Exception as e:
        db.rollback()
        raise e


def modify_apikey(
    db: Session, id: str, user_id: str, name: Optional[str] = None, description: Optional[str] = None, expire_at: Optional[datetime] = None
) -> Optional[UserApiKey]:
    """
    Modify fields of an existing API key by id, with user permission check.
    Args:
        db (Session): SQLAlchemy session
        id (str): API key id (required)
        user_id (str): User ID (required)
        name (str): New name (optional)
        description (str): New description (optional)
        expire_at (datetime): New expiration time (optional)
    Returns:
        UserApiKey: The updated API key object
    """
    user_apikey = db.query(UserApiKey).filter(UserApiKey.id == id).first()
    if not user_apikey or user_apikey.user_id != user_id:
        return None
    if name is not None:
        user_apikey.name = name
    if description is not None:
        user_apikey.description = description
    if expire_at is not None:
        user_apikey.expire_at = expire_at
    user_apikey.updated_at = datetime.now(timezone.utc)
    try:
        db.commit()
        db.refresh(user_apikey)
        return user_apikey
    except Exception as e:
        db.rollback()
        raise e


def delete_apikey(db: Session, id: str, user_id: str) -> Optional[UserApiKey]:
    """
    Delete (physical) an API key by id, with user permission check.
    Args:
        db (Session): SQLAlchemy session
        id (str): API key id
        user_id (str): User ID (required)
    Returns:
        UserApiKey: The deleted API key object, or None if not found or no permission
    """
    user_apikey = db.query(UserApiKey).filter(UserApiKey.id == id).first()
    if not user_apikey or user_apikey.user_id != user_id:
        return None
    try:
        db.delete(user_apikey)
        db.commit()
        return user_apikey
    except Exception as e:
        db.rollback()
        raise e


def get_user_apikey_list(db: Session, user_id: str) -> list[UserApiKey]:
    """
    Get all API keys for a user by user_id.
    Args:
        db (Session): SQLAlchemy session
        user_id (str): User ID
    Returns:
        list[UserApiKey]: List of API key objects
    """
    return db.query(UserApiKey).filter(UserApiKey.user_id == user_id).all()
