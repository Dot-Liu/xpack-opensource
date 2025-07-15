from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.response.user_response import UserResponse
from services.common.response.user_wallet_response import UserWalletResponse

router = APIRouter()


@router.get("/", response_model=dict)
def get_user(request: Request, db: Session = Depends(get_db)):
    """
    Retrieve user information from the request and return a formatted response.
    Args:
        request (Request): The incoming request object containing user context.
        db (Session, optional): Database session dependency.
    Returns:
        Response: Success response with user details if found, otherwise error response.
    """
    user_response = UserResponse()
    user_wallet_resp = UserWalletResponse()
    user_wallet_resp.balance = 0.00

    user = request.scope.get("user")
    if user:
        user_response.user_id = user.id
        user_response.name = user.name
        user_response.email = user.email
        user_response.created_at = user.created_at
        user_response.wallet = user_wallet_resp
        return ResponseUtils.success(user_response)
    return ResponseUtils.error(message="not found user", code=500)
