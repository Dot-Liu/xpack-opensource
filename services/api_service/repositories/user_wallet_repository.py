"""
用户钱包仓储类 - API服务中使用
"""
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from services.common.models.user_wallet import UserWallet


class UserWalletRepository:
    """用户钱包仓储类"""
    
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str) -> UserWallet:
        """
        创建用户钱包
        
        Args:
            user_id: 用户ID
            
        Returns:
            UserWallet: 创建的钱包实例
        """
        wallet = UserWallet(
            id=str(uuid.uuid4()),
            user_id=user_id,
            balance=0.0,
            frozen_balance=0.0,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(wallet)
        self.db.commit()
        self.db.refresh(wallet)
        return wallet

    def get_by_user_id(self, user_id: str) -> Optional[UserWallet]:
        """
        根据用户ID获取钱包
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[UserWallet]: 钱包实例，不存在则返回None
        """
        return self.db.query(UserWallet).filter(UserWallet.user_id == user_id).first()

    def update_balance(self, user_id: str, new_balance: float) -> bool:
        """
        更新用户余额
        
        Args:
            user_id: 用户ID
            new_balance: 新余额
            
        Returns:
            bool: 更新是否成功
        """
        wallet = self.get_by_user_id(user_id)
        if wallet:
            wallet.balance = new_balance
            # updated_at字段由数据库自动更新，不需要手动设置
            self.db.commit()
            return True
        return False
