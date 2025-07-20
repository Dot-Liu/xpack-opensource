class RedisKeys:

    @staticmethod
    def all_users_key() -> str:
        return "xpack:all_users"

    @staticmethod
    def user_access_token_key(token: str) -> str:
        """Generate token cache key"""
        return f"xpack:user_access_token:{token}"

    @staticmethod
    def user_key(user_id: str) -> str:
        """Generate user cache key"""
        return f"xpack:user:{user_id}"

    @staticmethod
    def email_login_captcha(email: str) -> str:
        return f"xpack:user:login:email:{email}"

    @staticmethod
    def parse_openapi_key(parse_id: str) -> str:
        """Generate OpenAPI parse result cache key"""
        return f"xpack:openapi:parse:{parse_id}"

    @staticmethod
    def sys_config_key(config_key: str) -> str:
        """Generate system config cache key"""
        return f"xpack:sys_config:{config_key}"
