from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.response.user_response import UserResponse
from services.common.response.user_wallet_response import UserWalletResponse
from services.admin_service.utils.user_utils import UserUtils

router = APIRouter()


@router.get("/", response_model=dict)
def get_user(request: Request, db: Session = Depends(get_db)):
    user_response = UserResponse()
    user_wallet_resp = UserWalletResponse()
    user_wallet_resp.balance = 0.00

    user = UserUtils.get_request_user(request)
    if user:
        user_response.user_id = user.id
        user_response.name = user.name
        user_response.email = user.email
        user_response.created_at = getattr(user, "created_at", None)
        user_response.wallet = user_wallet_resp
        return ResponseUtils.success(user_response)
    return ResponseUtils.error(message="not found user", code=500)
