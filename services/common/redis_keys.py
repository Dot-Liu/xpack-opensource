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

    @staticmethod
    def email_login_captcha(email: str) -> str:
        return f"xpack:user:login:email:{email}"

    @staticmethod
    def parse_openapi_key(parse_id: str) -> str:
        """
        生成OpenAPI解析结果缓存key

        Args:
            parse_id: 解析ID

        Returns:
            str: OpenAPI解析结果缓存key
        """
        return f"xpack:openapi:parse:{parse_id}"
