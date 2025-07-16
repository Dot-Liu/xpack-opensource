from sqlalchemy.orm import Session
from typing import Optional
from services.common.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create(self, email: str, register_type: str, role_id: int = 2) -> Optional[User]:
        from uuid import uuid4
        from services.common.models.user import RegisterType
        
        name = email.split("@")[0] if "@" in email else email

        user = User(
            id=str(uuid4()),
            name=name,
            email=email,
            avatar=None,
            is_active=1,
            is_deleted=0,
            register_type=RegisterType(register_type),
            role_id=role_id,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
