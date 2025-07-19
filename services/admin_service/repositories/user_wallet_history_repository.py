import logging
from typing import Optional
from sqlalchemy.orm import Session
from services.common.models.user_wallet_history import UserWalletHistory
from services.common.models.user_wallet import UserWallet
from services.common.models.user_wallet_history import TransactionType, PaymentMethod
from uuid import uuid4
from datetime import datetime, timezone


class UserWalletHistoryRepository:

    logging = logging.getLogger(__name__)

    def __init__(self, db: Session):
        self.db = db

    def add_deposit(self, user_id: str, amount: float, payment_method: str) -> UserWalletHistory:
        now = datetime.now(timezone.utc)
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
            created_at=now,
            updated_at=now,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def add_refund(self, user_id: str, amount: float, payment_method: str, transaction_id: str) -> UserWalletHistory:
        now = datetime.now(timezone.utc)
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
            created_at=now,
            updated_at=now,
        )
        self.db.add(history)
        self.db.commit()
        self.db.refresh(history)
        return history

    def deposit_complete(self, id: str, transaction_id: str) -> bool:
        """
        标记充值订单为已完成，并安全更新balance_after。
        :param id: user_wallet_history 的主键 id
        :param transaction_id: 支付平台流水号，可选
        :return: True=成功，False=未找到或失败
        """
        try:
            obj = self.db.query(UserWalletHistory).filter(UserWalletHistory.id == id).with_for_update().first()
            if not obj:
                self.logging.error(f"UserWalletHistory not found: id={id}")
                return False

            # 检查订单是否已经完成，避免重复处理
            if obj.status == 1:
                self.logging.warning(f"Order already completed: id={id}")
                return True

            # 只处理充值类型的订单
            if obj.type != TransactionType.DEPOSIT:
                self.logging.error(f"Order type is not deposit: id={id}, type={obj.type}")
                return False

            wallet = self.db.query(UserWallet).filter(UserWallet.user_id == obj.user_id).with_for_update().first()
            if not wallet:
                self.logging.error(f"UserWallet not found: user_id={obj.user_id}")
                return False

            # 更新钱包余额和订单状态
            wallet.balance = float(wallet.balance) + float(obj.amount)
            obj.status = 1  # 1=completed
            obj.balance_after = float(wallet.balance)
            obj.transaction_id = transaction_id

            self.db.commit()
            self.logging.info(f"Deposit completed successfully: id={id}, amount={obj.amount}, new_balance={wallet.balance}")
            return True

        except Exception as e:
            self.logging.error(f"Error completing deposit: id={id}, error={str(e)}")
            self.db.rollback()
            return False

    def success_order_list(self, offset: int, limit: int) -> tuple[int, list[UserWalletHistory]]:
        """
        订单列表
        :return:
        """
        total = self.db.query(UserWalletHistory).filter(UserWalletHistory.status == 1).count()
        if total < offset:
            return total, []
        history = (
            self.db.query(UserWalletHistory)
            .filter(UserWalletHistory.status == 1)
            .order_by(UserWalletHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )
        return total, history

    def get_by_id(self, history_id: str) -> Optional[UserWalletHistory]:
        """
        根据ID获取用户钱包历史记录
        :param history_id: 历史记录ID
        :return: UserWalletHistory对象或None
        """
        return self.db.query(UserWalletHistory).filter(UserWalletHistory.id == history_id).first()

    def add_consume_record(self, wallet_history: UserWalletHistory) -> Optional[UserWalletHistory]:
        """
        添加消费记录

        Args:
            wallet_history: 钱包历史记录对象

        Returns:
            Optional[UserWalletHistory]: 创建的记录，失败返回None
        """
        try:
            # 不需要手动设置 created_at 和 updated_at，让数据库自动处理
            self.db.add(wallet_history)
            self.db.commit()
            self.db.refresh(wallet_history)
            return wallet_history
        except Exception as e:
            self.logging.error(f"添加消费记录失败: {str(e)}")
            self.db.rollback()
            return None
