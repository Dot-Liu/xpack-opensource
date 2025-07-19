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
from services.admin_service.repositories.user_repository import UserRepository
from services.admin_service.repositories.user_wallet_repository import UserWalletRepository
from services.admin_service.repositories.user_wallet_history_repository import UserWalletHistoryRepository
from services.admin_service.services.payment_channel_service import PaymentChannelService

logger = logging.getLogger(__name__)

class PaymentService:

    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)
        self.user_wallet_repository = UserWalletRepository(db)
        self.user_wallet_history_repository = UserWalletHistoryRepository(db)
        self.payment_channel_service = PaymentChannelService(db)

    def _get_stripe_config(self) -> Optional[dict]:
        """
        获取 Stripe 配置
        
        Returns:
            Optional[dict]: Stripe 配置信息，包含 secret 和 webhook_secret
        """
        return self.payment_channel_service.get_stripe_config()

    def _configure_stripe_key(self) -> bool:
        """
        配置 Stripe API Key
        
        Returns:
            bool: 配置是否成功
        """
        stripe_config = self._get_stripe_config()
        if not stripe_config:
            logger.error("无法获取 Stripe 配置")
            return False
        
        stripe.api_key = stripe_config.get("secret")
        return True

    logging = logging.getLogger(__name__)

    def create_stripe_payment_link(self, user_id: str, amount: float, currency: str = "usd") -> Optional[dict]:
        # 配置 Stripe API Key
        if not self._configure_stripe_key():
            raise RuntimeError("Stripe 配置错误")
        
        # get user information
        user = self.user_repository.get_by_id(user_id)
        if not user:
            logger.error(f"User with ID {user_id} not found.")
            raise ValueError("User not found.")

        # create a new user wallet history entry for the deposit
        user_wallet_history = self.user_wallet_history_repository.add_deposit(user_id=user_id, amount=amount, payment_method="stripe")
        if user_wallet_history is None:
            logger.error("Failed to create user wallet history for deposit.")
            raise RuntimeError("Failed to create payment.")

        # create Stripe Checkout Session
        params = {
            "success_url": Config.PAY_SUCCESS_URL,
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
            return {"payment_link": session.url, "payment_id": user_wallet_history.id}
        except Exception as e:
            raise RuntimeError(f"Failed to create payment URL: {str(e)}")

    def stripe_payment_callback(self, payload: str, sig_header: str) -> bool:
        # 获取 Stripe 配置
        stripe_config = self._get_stripe_config()
        if not stripe_config:
            logger.error("无法获取 Stripe 配置，无法验证 webhook")
            return False
        
        webhook_secret = stripe_config.get("webhook_secret")
        if not webhook_secret:
            logger.error("Stripe webhook_secret 配置缺失")
            return False
        
        try:
            # 验证 Webhook 签名
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        except Exception as e:
            logger.error("Invalid payload or signature")
            return False

        # 处理支付成功事件
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            payment_id = session.get("client_reference_id")
            customer_email = session.get("customer_email")
            amount = session.get("amount_total") / 100  # 转换为实际金额
            currency = session.get("currency")
            payment_intent_id = session.get("payment_intent")

            logger.info(f"Payment succeeded: payment_id={payment_id}, email={customer_email}, amount={amount} {currency}")

            # 触发发货逻辑（示例）
            try:
                return self.user_wallet_history_repository.deposit_complete(payment_id, payment_intent_id)
            except Exception as e:
                logger.error(f"Failed to fulfill order for payment_id={payment_id}: {str(e)}")
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
