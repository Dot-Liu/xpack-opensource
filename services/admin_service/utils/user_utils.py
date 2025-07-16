from services.common.models.user import User


class UserUtils:
    @staticmethod
    def get_request_user(request) -> User:
        """统一获取 request 中的 user 对象"""
        return request.scope.get("user")

    @staticmethod
    def get_request_user_id(request) -> str:
        """获取 request 中的 user_id，获取不到则抛出异常"""
        user = UserUtils.get_request_user(request)
        if not user or not getattr(user, "id", None):
            raise ValueError("User not found in request or user_id missing")
        return user.id
