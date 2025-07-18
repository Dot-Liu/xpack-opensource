from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi import Depends
from services.admin_service.services.user_service import UserService
from services.admin_service.services.user_wallet_service import UserWalletService
from services.common.database import get_db
from services.common.models.user import User
from services.common.response.user_manager_response import UserManagerResponse
from services.common.utils.response_utils import ResponseUtils

router = APIRouter()

def get_user_wallet_service(db: Session = Depends(get_db)) -> UserWalletService:
    return UserWalletService(db)

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)

@router.delete("/account",summary="delete user")
async def delete_user(
    id: str, 
    user_service: UserService = Depends(get_user_service),
):
    """
    Delete user by id
    
    Args:
        id (str): User id
        db (Session): Database session
        
    Returns:
        bool: True if deletion was successful, False otherwise
    """

    user = user_service.delete(id)
    if not user:
        return ResponseUtils.error(message="delete user failed, user not found")
    return ResponseUtils.success(data=UserManagerResponse(**user.__dict__))

@router.get("/account/list",summary="get user list")
async def get_user_list(
    page: int = Query(1, description="当前页码"),
    page_size: int = Query(15, description="当前页面数据条数"),
    user_service: UserService = Depends(get_user_service),
    user_wallet_service: UserWalletService = Depends(get_user_wallet_service)
):
    """
    Get User List
    
    Args:
        page (Optional[int], optional): Current page number. Defaults to 1.
        page_size (Optional[int], optional): Number of items per page. Defaults to 10.
        db (Session, optional): Database session dependency.
        
    Returns:
        dict: A dictionary containing user list, pagination information, and success code.
    """
    # 计算偏移量
    skip = (page - 1) * page_size
    
    total,users = user_service.get_user_list(skip,page_size)
    
    # 转换用户数据为列表
    user_list = []
    for user in users:
        wallet = user_wallet_service.get_by_user_id(user.id)
        user_list.append({
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
            "balance": wallet.balance if wallet else 0
        })
    
    return ResponseUtils.success_page(data=user_list, total=total, page_num=page, page_size=page_size)
     
