from sqlalchemy.orm import Session
from services.common.models.user import User
from services.common.redis import redis_client
from services.common.redis_keys import RedisKeys
import json


def get_all_users(db: Session):
    cached_users = redis_client.get(RedisKeys.all_users_key())
    if cached_users:
        print("cached_users", cached_users)
        return json.loads(cached_users)

    try:
        users = db.query(User).all()
        user_data = [
            {"id": user.id, "name": user.name, "email": user.email} for user in users
        ]
        redis_client.set(RedisKeys.all_users_key(), json.dumps(user_data), ex=3600)
        return user_data
    except Exception as e:
        # 如果数据库查询失败，返回空列表
        print(f"Database query error: {e}")
        return []
