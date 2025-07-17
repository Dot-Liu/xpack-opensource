import logging
from sqlalchemy.orm import Session
from typing import Optional
from services.common.database import SessionLocal
from datetime import datetime
from services.admin_service.repositories.payment_channel_repository import PaymentChannelRepository
from services.common.models.payment_channel import PaymentChannel

class PaymentChannelService:
    def __init__(self, db: Session = SessionLocal()):
        self.db = db
        self.payment_channel_repository = PaymentChannelRepository(db)
    def list(self) -> tuple[int,list[PaymentChannel]]:
        return self.payment_channel_repository.payment_channel_list()
    def get(self, id: str) -> Optional[PaymentChannel]:
        return self.payment_channel_repository.payment_channel_get(id)
    def update_status(self, id: str, status: int) -> Optional[PaymentChannel]:
        return self.payment_channel_repository.update_status(id, status)
    def update_config(self, id: str, config: str) -> Optional[PaymentChannel]:
        return self.payment_channel_repository.update_config(id, config)