"""
User API key repository class - used in API service
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from services.common.models.user_apikey import UserApiKey


class UserApiKeyRepository:
    """User API key repository class"""
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_apikey(self, apikey: str) -> Optional[UserApiKey]:
        """
        Query user API key info by API key
        
        Args:
            apikey: API key
            
        Returns:
            Optional[UserApiKey]: User API key info, returns None if not exists
        """
        return self.db.query(UserApiKey).filter(UserApiKey.apikey == apikey).first()
    
    def is_apikey_valid(self, apikey: str) -> bool:
        """
        Check if API key is valid
        
        Args:
            apikey: API key
            
        Returns:
            bool: Whether valid
        """
        user_apikey = self.get_by_apikey(apikey)
        if not user_apikey:
            return False
            
        # Check if expired
        if user_apikey.expire_at:
            # Ensure timezone consistency: if database time has no timezone info, assume it's UTC time
            if user_apikey.expire_at.tzinfo is None:
                # Database time has no timezone info, assume UTC
                expire_at_utc = user_apikey.expire_at.replace(tzinfo=timezone.utc)
            else:
                expire_at_utc = user_apikey.expire_at
                
            if expire_at_utc < datetime.now(timezone.utc):
                return False
            
        return True
