from sqlalchemy.orm import Session
from typing import Optional
from services.common.database import SessionLocal

from services.common.models.sys_config import SysConfig
from services.admin_service.repositories.sys_config_repository import SysConfigRepository

class SysConfigService:
    def __init__(self, db: Session = SessionLocal()):
        self.sys_config_repository = SysConfigRepository(db)
    def get_value_by_key(self, key: str) -> Optional[str]:
        return self.sys_config_repository.get_value_by_key(key)
    def delete_by_key(self, key: str) -> bool:
        return self.sys_config_repository.delete_by_key(key)
    def set_value_by_key(self, key: str, value: str,description:str) -> Optional[SysConfig]:
        return self.sys_config_repository.set_value_by_key(key=key,value=value,description=description)