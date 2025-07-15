from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from services.admin_service.services import user as user_service
from services.common.database import get_db
from pydantic import BaseModel

router = APIRouter()

class UserResponse(BaseModel):
    id: int
    name: str
    email: str

class CurrentUserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    user_type: str

@router.get("/all-users", response_model=list[UserResponse])
def get_all_users(db: Session = Depends(get_db)):
    return user_service.get_all_users(db)

@router.get("/current-user", response_model=CurrentUserResponse)
def get_current_user(request: Request):
    """获取当前认证用户的信息"""
    user = request.scope.get("user")
    if not user:
        return {"error": "User not found"}
    
    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "user_type": user.user_type.value
    }