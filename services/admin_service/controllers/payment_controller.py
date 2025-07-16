from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
import asyncio

from services.common.database import get_db
from services.common.utils.response_utils import ResponseUtils
from services.admin_service.services import payment_service

router = APIRouter()


class CreatePaymentLinkRequest(BaseModel):
    amount: float
    currency: str = "usd"
    payment_method: str = "stripe"


@router.post("/create-payment-link", response_model=dict)
def create_payment_link(request: Request, body: CreatePaymentLinkRequest, db: Session = Depends(get_db)):
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
        payment_link = payment_service.create_stripe_payment_link(db=db, user_id=user.id, amount=body.amount, currency=body.currency)
        return ResponseUtils.success({"payment_link": payment_link})
    except Exception as e:
        return ResponseUtils.error(message=str(e), code=500)


@router.post("/callback-stripe", response_model=dict)
async def callback_stripe(request: Request, db: Session = Depends(get_db)):
    payload = (await request.body()).decode("utf-8")
    sig_header = request.headers.get("Stripe-Signature") or ""
    result = payment_service.stripe_payment_callback(db, payload, sig_header)
    if result:
        return ResponseUtils.success()
    else:
        return ResponseUtils.error(message="Stripe callback failed", code=500)
