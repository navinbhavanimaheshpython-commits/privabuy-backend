import stripe
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/payments", tags=["payments"])
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class CreatePaymentIntent(BaseModel):
    amount: int  # in cents — 25000 for $250, 50000 for $500
    currency: str = "usd"
    description: str = ""

@router.post("/create-intent")
async def create_payment_intent(body: CreatePaymentIntent):
    try:
        intent = stripe.PaymentIntent.create(
            amount=body.amount,
            currency=body.currency,
            description=body.description,
            automatic_payment_methods={"enabled": True},
        )
        return {"client_secret": intent.client_secret, "payment_intent_id": intent.id}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/confirm/{payment_intent_id}")
async def confirm_payment(payment_intent_id: str):
    try:
        intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        return {"status": intent.status, "amount": intent.amount}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))