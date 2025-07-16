import stripe
import logging
from typing import Optional
from sqlalchemy.orm import Session
import stripe.error
from services.admin_service.services import user_service
from services.admin_service.services import user_wallet_history_service
from services.common.models.user_wallet import UserWallet
from services.common.models.user_wallet_history import UserWalletHistory
from services.common.config import Config

logging = logging.getLogger(__name__)

stripe.api_key = (
    "sk_test_51QwyFqLRsT5POHCbnAJ7vyA0P8AvAu3rXOcPkCRbIzKziocSg3DALbKO94kaGiXqpMoqrqp1SXJSbOIqRguxMXAu00pfLTg0XN"  # Set your Stripe API key
)
stripe_webhook_secret = "whsec_P0ZDR8Bzwen3YnzGUzfW29mnPJSypnGa"  # Set your Stripe webhook secret


def create_stripe_payment_link(db: Session, user_id: str, amount: float, currency: str = "usd") -> Optional[str]:
    """
    Create a Stripe payment intent for the given amount and currency.

    Args:
        amount (float): The amount to charge in the smallest currency unit (e.g., cents).
        currency (str): The currency in which the payment is made. Default is 'usd'.

    Returns:
        str: The ID of the created payment intent.
    """

    # get user information
    user = user_service.get_user(db, user_id)
    if not user:
        logging.error(f"User with ID {user_id} not found.")
        raise ValueError("User not found.")

    # create a new user wallet history entry for the deposit
    user_wallet_history = user_wallet_history_service.add_deposit(db=db, user_id=user_id, amount=amount, payment_method="stripe")
    if user_wallet_history is None:
        logging.error("Failed to create user wallet history for deposit.")
        raise RuntimeError("Failed to create payment.")

    # create Stripe Checkout Session
    params = {
        "success_url": Config.pay_success_url,
        "cancel_url": Config.pay_cancel_url,
        "client_reference_id": user_wallet_history.id,
        "line_items": [
            {
                "price_data": {
                    "currency": currency,
                    "product_data": {"name": "One-Time Payment"},
                    "unit_amount": int(amount * 100),  # 金额转换为分（注意：某些货币如 JPY 不需要乘 100）
                },
                "quantity": 1,
            }
        ],
        "customer_email": user.email,
        "mode": "payment",
    }

    try:
        session = stripe.checkout.Session.create(**params)
        return session.url
    except Exception as e:
        raise RuntimeError(f"Failed to create payment URL: {str(e)}")


def stripe_payment_callback(db: Session, payload: str, sig_header: str) -> bool:
    try:
        # 验证 Webhook 签名
        event = stripe.Webhook.construct_event(payload, sig_header, stripe_webhook_secret)
    except Exception as e:
        logging.error("Invalid payload or signature")
        return False

    # 处理支付成功事件
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        payment_id = session.get("client_reference_id")
        customer_email = session.get("customer_email")
        amount = session.get("amount_total") / 100  # 转换为实际金额
        currency = session.get("currency")
        payment_intent_id = session.get("payment_intent")

        logging.info(f"Payment succeeded: payment_id={payment_id}, email={customer_email}, amount={amount} {currency}")

        # 触发发货逻辑（示例）
        try:
            return deposit_complete(db, payment_id, payment_intent_id)
        except Exception as e:
            logging.error(f"Failed to fulfill order for payment_id={payment_id}: {str(e)}")
            return False

    # # 处理退款事件
    # elif event["type"] == "charge.refunded":
    #     charge = event["data"]["object"]
    #     payment_id = charge.get("payment_intent")
    #     amount_refunded = charge.get("amount_refunded") / 100  # 转换为实际金额
    #     currency = charge.get("currency")

    #     logging.info(f"Refund processed: payment_id={payment_id}, amount_refunded={amount_refunded} {currency}")

    #     # 触发退款处理逻辑（示例）
    #     try:
    #         # process_refund(payment_id, amount_refunded)
    #         logging.info(f"Refund processed for payment_id={payment_id}")
    #     except Exception as e:
    #         logging.error(f"Failed to process refund for payment_id={payment_id}: {str(e)}")
    #         return False

    return False


def deposit_complete(db: Session, id: str, transaction_id: str) -> bool:
    """
    标记充值订单为已完成，并安全更新balance_after。
    :param db: SQLAlchemy Session
    :param id: user_wallet_history 的主键 id
    :param transaction_id: 支付平台流水号，可选
    :return: True=成功，False=未找到或失败
    """

    obj = db.query(UserWalletHistory).filter(UserWalletHistory.id == id).with_for_update().first()
    if not obj:
        logging.error(f"UserWalletHistory not found: id={id}")
        return False
    wallet = db.query(UserWallet).filter(UserWallet.user_id == obj.user_id).with_for_update().first()
    if not wallet:
        logging.error(f"UserWallet not found: user_id={obj.user_id}")
        return False
    wallet.balance = float(wallet.balance) + float(obj.amount)
    obj.status = 1  # 1=completed
    obj.balance_after = float(wallet.balance)
    obj.transaction_id = transaction_id
    db.commit()
    return True
