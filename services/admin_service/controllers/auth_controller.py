from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.response.user_response import UserResponse
from services.common.response.user_wallet_response import UserWalletResponse
from services.admin_service.services import auth_service

router = APIRouter()


@router.get("/auth/email/sign", response_model=dict)
def email_login(email: str, captcha: str, db: Session = Depends(get_db)):
    token = auth_service.email_login(db, email, captcha)
    if token:
        return ResponseUtils.success({"token": token})
    else:
        return ResponseUtils.error(message="login failed", code=401)


@router.post("/auth/email/send-captcha", response_model=dict)
def email_login_send_captcha(email: str):
    if auth_service.send_email_login_captcha(email):
        return ResponseUtils.success()
    else:
        return ResponseUtils.error(message="send email fail")
