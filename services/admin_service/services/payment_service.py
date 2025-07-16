import stripe
import uuid
import logging
from typing import Optional
from sqlalchemy.orm import Session
from dataclasses import dataclass
from services.admin_service.services import user_service
from services.admin_service.services import user_wallet_history_service
from services.common.config import Config

logging = logging.getLogger(__name__)

stripe.api_key = "sk_test_51QwyFqLRsT5POHCbnAJ7vyA0P8AvAu3rXOcPkCRbIzKziocSg3DALbKO94kaGiXqpMoqrqp1SXJSbOIqRguxMXAu00pfLTg0XN"  # Set your Stripe API key


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
