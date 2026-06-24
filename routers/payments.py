import stripe
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import asyncpg

router = APIRouter(prefix="/payments", tags=["payments"])
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ─── DB dependency (matches your existing pattern across other routers) ───────
async def get_db():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:
        yield conn
    finally:
        await conn.close()


# ─── Models ───────────────────────────────────────────────────────────────────

class CreatePaymentIntent(BaseModel):
    amount: int = Field(..., gt=0, description="Amount in cents — must be > 0")
    currency: str = "usd"
    description: str = ""

class DealerFeePayment(BaseModel):
    transaction_id: str = Field(..., min_length=1, description="Must be a real transaction ID")
    dealer_id: str = Field(..., min_length=1, description="Must be a real dealer ID")


# ─── Routes ───────────────────────────────────────────────────────────────────

@router.post("/create-intent")
async def create_payment_intent(body: CreatePaymentIntent):
    """
    Generic intent — kept for internal/admin use only.
    Dealer auction fees must use /dealer-fee instead.
    Do NOT call this from the frontend for dealer payments.
    """
    if body.amount == 85000:
        raise HTTPException(
            status_code=400,
            detail="Use /payments/dealer-fee for dealer auction fee payments — not /create-intent."
        )
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


@router.post("/dealer-fee")
async def pay_dealer_fee(body: DealerFeePayment, db=Depends(get_db)):
    """
    Charges the dealer $850 total:
      - $600 dealer platform fee
      - $250 seller fee (bundled — dealer pays both)

    Guards:
      1. Verifies the transaction exists in DB before touching Stripe
      2. Verifies it hasn't already been paid (prevents double-charge)
      3. Idempotency key = transaction_id (Stripe deduplicates retries)
    """

    # ── Guard 1: transaction must exist ──────────────────────────────────────
    txn = await db.fetchrow(
        "SELECT transaction_id, dealer_fee_paid, status FROM transactions WHERE transaction_id = $1",
        body.transaction_id
    )
    if not txn:
        raise HTTPException(
            status_code=404,
            detail=f"Transaction {body.transaction_id} not found. Cannot charge before a transaction exists."
        )

    # ── Guard 2: block double-charge ─────────────────────────────────────────
    if txn["dealer_fee_paid"]:
        raise HTTPException(
            status_code=409,
            detail="Dealer fee has already been paid for this transaction."
        )

    # ── Guard 3: transaction must be in the right state ──────────────────────
    if txn["status"] != "awaiting_dealer_payment":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot charge fee — transaction status is '{txn['status']}', expected 'awaiting_dealer_payment'."
        )

    # ── Create Stripe intent with idempotency key ─────────────────────────────
    try:
        intent = stripe.PaymentIntent.create(
            amount=85000,       # $850.00 — $600 dealer + $250 seller fee
            currency="usd",
            description="PrivaBuy Dealer Fee ($600) + Seller Fee ($250)",
            metadata={
                "transaction_id": body.transaction_id,
                "dealer_id": body.dealer_id,
                "dealer_fee": 60000,   # $600.00 in cents
                "seller_fee": 25000,   # $250.00 in cents
            },
            automatic_payment_methods={"enabled": True},
            idempotency_key=body.transaction_id,  # Stripe deduplicates retries on same txn
        )
        return {"client_secret": intent.client_secret, "payment_intent_id": intent.id}
    except stripe.error.IdempotencyError:
        # A prior intent was already created for this transaction — return its existing secret
        raise HTTPException(
            status_code=409,
            detail="A payment intent already exists for this transaction. Check Stripe dashboard."
        )
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))