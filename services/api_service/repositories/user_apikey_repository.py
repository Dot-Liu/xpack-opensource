"""
用户API密钥仓储类 - API服务中使用
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from services.common.models.user_apikey import UserApiKey


class UserApiKeyRepository:
    """用户API密钥仓储类"""
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_apikey(self, apikey: str) -> Optional[UserApiKey]:
        """
        根据API密钥查询用户API密钥信息
        
        Args:
            apikey: API密钥
            
        Returns:
            Optional[UserApiKey]: 用户API密钥信息，如果不存在则返回None
        """
        return self.db.query(UserApiKey).filter(UserApiKey.apikey == apikey).first()
    
    def is_apikey_valid(self, apikey: str) -> bool:
        """
        检查API密钥是否有效
        
        Args:
            apikey: API密钥
            
        Returns:
            bool: 是否有效
        """
        user_apikey = self.get_by_apikey(apikey)
        if not user_apikey:
            return False
            
        # 检查是否过期
        if user_apikey.expire_at:
            # 确保时区一致性：如果数据库中的时间没有时区信息，假设它是UTC时间
            if user_apikey.expire_at.tzinfo is None:
                # 数据库时间没有时区信息，假设为UTC
                expire_at_utc = user_apikey.expire_at.replace(tzinfo=timezone.utc)
            else:
                expire_at_utc = user_apikey.expire_at
                
            if expire_at_utc < datetime.now(timezone.utc):
                return False
            
        return True
