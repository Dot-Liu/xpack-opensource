import datetime
from services.common.response.user_wallet_response import UserWalletResponse
from pydantic import BaseModel
from typing import Optional


class UserResponse(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    wallet: Optional[UserWalletResponse] = None
