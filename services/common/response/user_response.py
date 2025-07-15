import datetime
from pydantic import BaseModel
from typing import Optional


class UserResponse(BaseModel):
    user_id: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
