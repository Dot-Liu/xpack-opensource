import logging
from sqlalchemy.orm import Session
from services.common.models.user_wallet_history import UserWalletHistory
from services.common.models.user_wallet import UserWallet
from services.common.models.user_wallet_history import TransactionType, PaymentMethod
from uuid import uuid4


class UserWalletHistoryRepository:

    logging = logging.getLogger(__name__)

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

    def deposit_complete(self, id: str, transaction_id: str) -> bool:
        """
        标记充值订单为已完成，并安全更新balance_after。
        :param db: SQLAlchemy Session
        :param id: user_wallet_history 的主键 id
        :param transaction_id: 支付平台流水号，可选
        :return: True=成功，False=未找到或失败
        """

        obj = self.db.query(UserWalletHistory).filter(UserWalletHistory.id == id).with_for_update().first()
        if not obj:
            logging.error(f"UserWalletHistory not found: id={id}")
            return False
        wallet = self.db.query(UserWallet).filter(UserWallet.user_id == obj.user_id).with_for_update().first()
        if not wallet:
            logging.error(f"UserWallet not found: user_id={obj.user_id}")
            return False
        wallet.balance = float(wallet.balance) + float(obj.amount)
        obj.status = 1  # 1=completed
        obj.balance_after = float(wallet.balance)
        obj.transaction_id = transaction_id
        self.db.commit()
        return True
    def success_order_list(self,offset:int,limit:int) -> tuple[int,list[UserWalletHistory]]:
        """
        订单列表
        :return: 
        """
        total = self.db.query(UserWalletHistory).filter(UserWalletHistory.status == 1).count()
        if total < offset:
            return total,[]
        history = self.db.query(UserWalletHistory).filter(UserWalletHistory.status == 1).order_by(UserWalletHistory.created_at.desc()).offset(offset).limit(limit).all()
        return total,history
