from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services.auth_service import AuthService
from services.admin_service.utils.user_utils import UserUtils

router = APIRouter()


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/email/sign", response_model=dict)
def email_login(body: dict = Body(...), auth_service: AuthService = Depends(get_auth_service)):
    email = body.get("email")
    captcha = body.get("captcha")
    if not email or not captcha:
        return ResponseUtils.error(message="email and captcha required", code=400)
    token = auth_service.email_login(email, captcha)
    if token:
        return ResponseUtils.success({"user_token": token})
    else:
        return ResponseUtils.error(message="login failed", code=401)


@router.post("/email/send_captcha", response_model=dict)
def email_login_send_captcha(body: dict = Body(...), auth_service: AuthService = Depends(get_auth_service)):
    email = body.get("email")
    if not email:
        return ResponseUtils.error(message="email required", code=400)
    if auth_service.send_email_login_captcha(email):
        return ResponseUtils.success()
    else:
        return ResponseUtils.error(message="send email fail")


@router.post("/account/sign", response_model=dict)
def account_login(body: dict = Body(...), auth_service: AuthService = Depends(get_auth_service)):
    name = body.get("name")
    password = body.get("password")
    if not name or not password:
        return ResponseUtils.error(message="account and password required", code=400)
    token = auth_service.email_login(name, password)
    if token:
        return ResponseUtils.success({"user_token": token})
    else:
        return ResponseUtils.error(message="login failed", code=401)


@router.delete("/auth/logout", response_model=dict)
def logout(request: Request, auth_service: AuthService = Depends(get_auth_service)):
    user_id = UserUtils.get_request_user_id(request)
    auth_service.logout(user_id)
    return ResponseUtils.success(message="Logout successful")
