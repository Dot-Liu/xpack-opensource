from sqlalchemy.orm import Session
from services.common.models.user_wallet_history import UserWalletHistory
from services.common.models.user_wallet_history import TransactionType, PaymentMethod
from uuid import uuid4


def add_deposit(db: Session, user_id: str, amount: float, payment_method: str) -> UserWalletHistory:
    """
    Add a deposit transaction to the user's wallet history.
    Args:
        db (Session): The database session.
        user_id (str): The ID of the user making the deposit.
        amount (float): The amount to deposit.
        payment_method (str): The payment method used for the deposit.
    Returns:
        UserWalletHistory: The created wallet history record.
    """

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
    db.add(history)
    db.commit()
    db.refresh(history)
    return history


def add_refund(db: Session, user_id: str, amount: float, payment_method: str, transaction_id: str) -> UserWalletHistory:
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
    db.add(history)
    db.commit()
    db.refresh(history)
    return history
