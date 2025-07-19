from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio
import logging

from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.common.utils.request_utils import RequestUtils
from services.admin_service.services.payment_service import PaymentService
from services.admin_service.services.user_wallet_history_service import UserWalletHistoryService

router = APIRouter()


def get_payment(db: Session = Depends(get_db)) -> PaymentService:
    return PaymentService(db)


def get_user_wallet_history(db: Session = Depends(get_db)) -> UserWalletHistoryService:
    return UserWalletHistoryService(db)


class CreatePaymentLinkRequest(BaseModel):
    amount: float
    currency: str = "usd"
    payment_method: str = "stripe"


@router.post("/create_payment_link", response_model=dict)
def create_payment_link(request: Request, body: CreatePaymentLinkRequest, payment: PaymentService = Depends(get_payment)):
    """
    Create a Stripe payment link for the user.

    Args:
        request (Request): The incoming request object containing user context.
        body (CreatePaymentLinkRequest): 请求体，包含金额和币种
        db (Session, optional): Database session dependency.

    Returns:
        Response: Success response with payment link if created, otherwise error response.
    """
    user = request.scope.get("user")
    if not user:
        return ResponseUtils.error(message="User not found", code=404)

    try:
        base_url = RequestUtils.get_real_base_url(request)
        logging.debug(f"base_url: {base_url}")
        payment_info = payment.create_stripe_payment_link(base_url, user_id=user.id, amount=body.amount, currency=body.currency)
        if payment_info:
            return ResponseUtils.success({"pay_url": payment_info.get("payment_link"), "payment_id": payment_info.get("payment_id")})
    except Exception as e:
        return ResponseUtils.error(message=str(e), code=500)


@router.post("/callback_stripe", response_model=dict)
async def callback_stripe(request: Request, payment: PaymentService = Depends(get_payment)):
    payload = (await request.body()).decode("utf-8")
    sig_header = request.headers.get("Stripe-Signature") or ""
    result = payment.stripe_payment_callback(payload, sig_header)
    if result:
        return ResponseUtils.success()
    else:
        return ResponseUtils.error(message="Stripe callback failed", code=500)


@router.get("/order_status", response_model=dict)
async def order_status(
    payment_id: str,
    get_user_wallet_history: UserWalletHistoryService = Depends(get_user_wallet_history),
):
    if get_user_wallet_history.check_order_complete(payment_id):
        return ResponseUtils.success({"status": 1})
    return ResponseUtils.success({"status": 0})
