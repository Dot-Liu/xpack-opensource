from fastapi import APIRouter, Depends, Request, Body
from sqlalchemy.orm import Session
from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.response.apikey_response import ApikeyResponse
from services.admin_service.services.user_apikey_service import UserApiKeyService
from services.admin_service.utils.user_utils import UserUtils

router = APIRouter()


def get_apikey_service(db: Session = Depends(get_db)) -> UserApiKeyService:
    return UserApiKeyService(db)


@router.post("/", summary="add apikey")
def add_apikey(request: Request, apikey_service: UserApiKeyService = Depends(get_apikey_service), body: dict = Body(...)):
    user_id = UserUtils.get_request_user_id(request)
    name = body.get("name")
    if not user_id or not name:
        return ResponseUtils.error(message="user_id and name are required")

    user_apikey = apikey_service.create(user_id=user_id, name=name)
    if not user_apikey:
        return ResponseUtils.error(message="Create failed")
    return ResponseUtils.success(data=ApikeyResponse(**user_apikey.__dict__))


@router.get("/user-apikey-list", summary="get user apikey list")
def get_user_apikey_list(request: Request, apikey_service: UserApiKeyService = Depends(get_apikey_service)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    if not user_id:
        return ResponseUtils.error(message="user_id is required")
    apikey_list = apikey_service.get_by_user_id(user_id)
    data = [ApikeyResponse(**item.__dict__) for item in apikey_list]
    return ResponseUtils.success(data=data)


@router.delete("/", summary="delete user apikey")
def delete_apikey(request: Request, apikey_service: UserApiKeyService = Depends(get_apikey_service), body: dict = Body(...)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    id = body.get("id")
    if not id or not user_id:
        return ResponseUtils.error(message="id and user_id are required")
    apikey_obj = apikey_service.delete(id, user_id)
    if not apikey_obj:
        return ResponseUtils.error(message="Delete failed or not found or no permission")
    return ResponseUtils.success(data=ApikeyResponse(**apikey_obj.__dict__))


@router.put("/", summary="modify user apikey")
def modify_apikey(request: Request, apikey_service: UserApiKeyService = Depends(get_apikey_service), body: dict = Body(...)):
    user = request.scope.get("user")
    user_id = user.id if user else None
    id = body.get("id")
    name = body.get("name")
    description = body.get("description")
    expire_at = body.get("expire_at")
    if not id or not user_id:
        return ResponseUtils.error(message="id and user_id are required")
    apikey_obj = apikey_service.modify(id, user_id, name=name, description=description, expire_at=expire_at)
    if not apikey_obj:
        return ResponseUtils.error(message="Modify failed or not found or no permission")
    return ResponseUtils.success(data=ApikeyResponse(**apikey_obj.__dict__))
