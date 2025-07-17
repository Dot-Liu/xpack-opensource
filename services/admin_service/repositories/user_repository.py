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
    
    def get_by_account(self, name: str) -> Optional[User]:
        return self.db.query(User).filter(User.name == name).first()

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

    def delete(self, user_id: str) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None
        user.is_deleted = 1
        self.db.commit()
        self.db.refresh(user)
        return user
    def get_user_list(self, offset: int, limit: int) -> tuple[int, list[User]]:
        total = self.db.query(User).filter(User.is_deleted == 0).count()

        users = self.db.query(User).filter(User.is_deleted == 0).offset(offset).limit(limit).all()
        return total, users
