from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from services.admin_service.services import user as user_service
from services.common.database import get_db
from pydantic import BaseModel
from services.common.utils.response_utils import ResponseUtils

router = APIRouter()

@router.get("/all-users", response_model=dict)
def get_all_users(db: Session = Depends(get_db)):
    return ResponseUtils.success(user_service.get_all_users(db))