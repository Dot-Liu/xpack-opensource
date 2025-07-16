from sqlalchemy.orm import Session
from services.common.models.user_wallet_history import UserWalletHistory
from services.admin_service.repositories.user_wallet_history_repository import UserWalletHistoryRepository


class UserWalletHistoryService:
    def __init__(self, db: Session):
        self.user_wallet_history_repository = UserWalletHistoryRepository(db)

    def add_deposit(self, user_id: str, amount: float, payment_method: str) -> UserWalletHistory:
        return self.user_wallet_history_repository.add_deposit(user_id, amount, payment_method)

    def add_refund(self, user_id: str, amount: float, payment_method: str, transaction_id: str) -> UserWalletHistory:
        return self.user_wallet_history_repository.add_refund(user_id, amount, payment_method, transaction_id)
