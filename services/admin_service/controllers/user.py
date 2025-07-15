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