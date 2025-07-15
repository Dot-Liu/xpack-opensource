from sqlalchemy.orm import Session
from services.common.models.user import User
from services.common.utils import hash_password
from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
from services.common.rabbitmq import rabbitmq_client
import json
from fastapi import HTTPException

def create_user(username: str, email: str, password: str, db: Session):
    cached_user = redis_client.get(RedisKeys.user_key(username))
    if cached_user:
        raise HTTPException(status_code=400, detail="Username already exists (cached)")

    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = hash_password(password)
    db_user = User(username=username, email=email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    user_data = {"id": db_user.id, "username": db_user.username, "email": db_user.email}
    redis_client.set(RedisKeys.user_key(db_user.username), json.dumps(user_data), ex=3600)
    redis_client.set(RedisKeys.user_id_key(db_user.id), json.dumps(user_data), ex=3600)
    rabbitmq_client.publish("user_events", json.dumps({"event": "user_created", "user_id": db_user.id}))

    return db_user

def get_user(user_id: int, db: Session):
    cached_user = redis_client.get(RedisKeys.user_id_key(user_id))
    if cached_user:
        return json.loads(cached_user)

    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = {"id": db_user.id, "username": db_user.username, "email": db_user.email}
    redis_client.set(RedisKeys.user_id_key(user_id), json.dumps(user_data), ex=3600)
    return user_data