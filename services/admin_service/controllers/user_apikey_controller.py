from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.response.apikey_response import ApikeyResponse
from services.admin_service.services import user_apikey_service

router = APIRouter()


# method=post path="/" desc="add apikey"
@router.post("/", summary="add apikey")
def add_apikey(request: Request, db: Session = Depends(get_db), body: dict = Body(...)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    name = body.get("name")
    if not user_id or not name:
        return ResponseUtils.error(message="user_id and name are required")
    apikey_obj = user_apikey_service.add_apikey(db, user_id, name)
    if not apikey_obj:
        return ResponseUtils.error(message="Create failed")
    return ResponseUtils.success(data=ApikeyResponse(**apikey_obj.__dict__))


# method=get path="/user-apikey-list" desc="get user apikey list"
@router.get("/user-apikey-list", summary="get user apikey list")
def get_user_apikey_list(request: Request, db: Session = Depends(get_db)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    if not user_id:
        return ResponseUtils.error(message="user_id is required")
    apikey_list = user_apikey_service.get_user_apikey_list(db, user_id)
    data = [ApikeyResponse(**item.__dict__) for item in apikey_list]
    return ResponseUtils.success(data=data)


# method=delete path="/" desc="delete user apikey"
@router.delete("/", summary="delete user apikey")
def delete_apikey(request: Request, db: Session = Depends(get_db), body: dict = Body(...)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    id = body.get("id")
    if not id or not user_id:
        return ResponseUtils.error(message="id and user_id are required")
    apikey_obj = user_apikey_service.delete_apikey(db, id, user_id)
    if not apikey_obj:
        return ResponseUtils.error(message="Delete failed or not found or no permission")
    return ResponseUtils.success(data=ApikeyResponse(**apikey_obj.__dict__))


# method=put path="/" desc="modify user apikey"
@router.put("/", summary="modify user apikey")
def modify_apikey(request: Request, db: Session = Depends(get_db), body: dict = Body(...)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    id = body.get("id")
    name = body.get("name")
    description = body.get("description")
    expire_at = body.get("expire_at")
    if not id or not user_id:
        return ResponseUtils.error(message="id and user_id are required")
    apikey_obj = user_apikey_service.modify_apikey(db, id, user_id, name=name, description=description, expire_at=expire_at)
    if not apikey_obj:
        return ResponseUtils.error(message="Modify failed or not found or no permission")
    return ResponseUtils.success(data=ApikeyResponse(**apikey_obj.__dict__))
