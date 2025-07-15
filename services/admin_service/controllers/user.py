from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.response.user_response import UserResponse

router = APIRouter()


@router.get("/user", response_model=dict)
def get_user(request: Request, db: Session = Depends(get_db)):
    user_response = UserResponse()

    user = request.scope.get("user")
    if user:
        user_response.user_id = user.user_id
        user_response.name = user.name
        user_response.email = user.email
        user_response.created_at = user.created_at
        return ResponseUtils.success(user_response)
    return ResponseUtils.error(message="not found user", code=500)
