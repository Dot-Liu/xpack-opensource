from sqlalchemy.orm import Session
from services.common.models.user_wallet_history import UserWalletHistory
from services.common.models.user_wallet_history import TransactionType, PaymentMethod
from uuid import uuid4


class UserWalletHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_deposit(self, user_id: str, amount: float, payment_method: str) -> UserWalletHistory:
        history = UserWalletHistory(
            id=str(uuid4()),
            user_id=user_id,
            payment_method=PaymentMethod(payment_method),
            amount=amount,
            balance_after=0.00,
            type=TransactionType.DEPOSIT,
            status=0,
            transaction_id=None,
            channel_user_id=None,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def add_refund(self, user_id: str, amount: float, payment_method: str, transaction_id: str) -> UserWalletHistory:
        history = UserWalletHistory(
            id=str(uuid4()),
            user_id=user_id,
            payment_method=PaymentMethod(payment_method),
            amount=amount,
            balance_after=0.00,
            type=TransactionType.REFUND,
            status=0,  # 2=已退款
            transaction_id=transaction_id,
            channel_user_id=None,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history
