class RedisKeys:
    
    @staticmethod
    def all_users_key() -> str:
        return "xpack:all_users"
    
    @staticmethod
    def user_access_token_key(token: str) -> str:
        """生成token缓存key"""
        return f"xpack:user_access_token:{token}"

    @staticmethod
    def user_key(user_id: str) -> str:
        """生成用户缓存key"""
        return f"xpack:user:{user_id}"
