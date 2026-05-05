from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import uuid
import asyncpg
import os

router = APIRouter(prefix="/transactions", tags=["transactions"])
DATABASE_URL = os.environ.get("DATABASE_URL")

async def get_db():
    return await asyncpg.connect(DATABASE_URL)

# ─────────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────────

class ProposeTimeSlotsRequest(BaseModel):
    transaction_id: str
    dealer_id: str
    slot_1: str  # ISO datetime string
    slot_2: str
    slot_3: str

class ConfirmSlotRequest(BaseModel):
    transaction_id: str
    seller_id: str
    chosen_slot: str  # one of slot_1/slot_2/slot_3

class PickupConfirmRequest(BaseModel):
    transaction_id: str
    dealer_id: str
    as_described: bool
    discrepancy_note: Optional[str] = None

class SellerPaymentConfirmRequest(BaseModel):
    transaction_id: str
    seller_id: str

class BillOfSaleAckRequest(BaseModel):
    transaction_id: str
    party: str  # "dealer" or "seller"

# ─────────────────────────────────────────────
#  CREATE TRANSACTION (called when seller accepts bid)
#  Call this from your existing offers/accept endpoint
# ─────────────────────────────────────────────

async def create_transaction(offer_id: str, car_id: str, dealer_id: str, seller_id: str, amount: float, db):
    """
    Called automatically when seller accepts a bid.
    Creates the transaction record and sets the 24hr dealer payment deadline.
    """
    transaction_id = str(uuid.uuid4())
    dealer_payment_deadline = datetime.utcnow() + timedelta(hours=24)

    await db.execute("""
        INSERT INTO transactions (
            transaction_id, offer_id, car_id, dealer_id, seller_id,
            amount, status,
            dealer_payment_deadline,
            dealer_fee_paid, seller_fee_paid,
            bill_of_sale_dealer_acked, bill_of_sale_seller_acked,
            created_at
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13)
    """,
        transaction_id, offer_id, car_id, dealer_id, seller_id,
        amount, "awaiting_dealer_payment",
        dealer_payment_deadline,
        False, False,
        False, False,
        datetime.utcnow()
    )
    return transaction_id


# ─────────────────────────────────────────────
#  GET TRANSACTION
# ─────────────────────────────────────────────

@router.get("/{transaction_id}")
async def get_transaction(transaction_id: str):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1",
            transaction_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return dict(row)
    finally:
        await db.close()


@router.get("/car/{car_id}")
async def get_transaction_by_car(car_id: str):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE car_id = $1 ORDER BY created_at DESC LIMIT 1",
            car_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="No transaction for this car")
        return dict(row)
    finally:
        await db.close()


@router.get("/dealer/{dealer_id}")
async def get_dealer_transactions(dealer_id: str):
    db = await get_db()
    try:
        rows = await db.fetch(
            """SELECT t.*, c.year, c.make, c.model, c.mileage
               FROM transactions t
               JOIN cars c ON t.car_id = c.id
               WHERE t.dealer_id = $1
               ORDER BY t.created_at DESC""",
            dealer_id
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


@router.get("/seller/{seller_id}")
async def get_seller_transactions(seller_id: str):
    db = await get_db()
    try:
        rows = await db.fetch(
            """SELECT t.*, c.year, c.make, c.model, c.mileage,
                      d.dealer_name, d.phone as dealer_phone, d.email as dealer_email
               FROM transactions t
               JOIN cars c ON t.car_id = c.id
               JOIN dealers d ON t.dealer_id = d.dealer_id
               WHERE t.seller_id = $1
               ORDER BY t.created_at DESC""",
            seller_id
        )
        return [dict(r) for r in rows]
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 1 → Dealer pays $600 (called after Stripe success)
#  Status: awaiting_dealer_payment → awaiting_bill_of_sale
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/dealer-paid")
async def mark_dealer_paid(transaction_id: str):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", transaction_id
        )
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Check 24hr deadline
        if datetime.utcnow() > row["dealer_payment_deadline"]:
            await db.execute(
                "UPDATE transactions SET status = $1 WHERE transaction_id = $2",
                "forfeited", transaction_id
            )
            raise HTTPException(status_code=400, detail="Payment deadline expired — bid forfeited")

        await db.execute(
            """UPDATE transactions
               SET dealer_fee_paid = TRUE,
                   dealer_paid_at = $1,
                   status = 'awaiting_bill_of_sale'
               WHERE transaction_id = $2""",
            datetime.utcnow(), transaction_id
        )
        return {"status": "awaiting_bill_of_sale", "message": "Payment confirmed. Bill of Sale is ready."}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 2 → Bill of Sale acknowledgment
#  Both dealer and seller must ack before moving on
#  Status: awaiting_bill_of_sale → awaiting_pickup_schedule (when both acked)
# ─────────────────────────────────────────────

@router.post("/bill-of-sale/acknowledge")
async def acknowledge_bill_of_sale(req: BillOfSaleAckRequest):
    db = await get_db()
    try:
        if req.party == "dealer":
            await db.execute(
                """UPDATE transactions SET bill_of_sale_dealer_acked = TRUE,
                   dealer_acked_at = $1 WHERE transaction_id = $2""",
                datetime.utcnow(), req.transaction_id
            )
        elif req.party == "seller":
            await db.execute(
                """UPDATE transactions SET bill_of_sale_seller_acked = TRUE,
                   seller_acked_at = $1 WHERE transaction_id = $2""",
                datetime.utcnow(), req.transaction_id
            )

        # Check if both have acked
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", req.transaction_id
        )
        if row["bill_of_sale_dealer_acked"] and row["bill_of_sale_seller_acked"]:
            await db.execute(
                "UPDATE transactions SET status = 'awaiting_pickup_schedule' WHERE transaction_id = $1",
                req.transaction_id
            )
            return {"status": "awaiting_pickup_schedule", "both_acked": True}

        return {"status": "awaiting_bill_of_sale", "both_acked": False,
                "waiting_on": "seller" if req.party == "dealer" else "dealer"}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 3a → Dealer proposes 3 pickup time slots
#  (within 5 business days)
#  Status stays: awaiting_pickup_schedule
# ─────────────────────────────────────────────

@router.post("/pickup/propose-slots")
async def propose_pickup_slots(req: ProposeTimeSlotsRequest):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", req.transaction_id
        )
        if not row or row["dealer_id"] != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        await db.execute(
            """UPDATE transactions
               SET pickup_slot_1 = $1, pickup_slot_2 = $2, pickup_slot_3 = $3,
                   slots_proposed_at = $4, status = 'awaiting_slot_confirmation'
               WHERE transaction_id = $5""",
            req.slot_1, req.slot_2, req.slot_3, datetime.utcnow(), req.transaction_id
        )
        return {"status": "awaiting_slot_confirmation", "message": "Slots sent to seller"}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 3b → Seller confirms a pickup slot
#  Status: awaiting_slot_confirmation → pickup_scheduled
# ─────────────────────────────────────────────

@router.post("/pickup/confirm-slot")
async def confirm_pickup_slot(req: ConfirmSlotRequest):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", req.transaction_id
        )
        if not row or row["seller_id"] != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        await db.execute(
            """UPDATE transactions
               SET confirmed_pickup_slot = $1,
                   slot_confirmed_at = $2,
                   status = 'pickup_scheduled'
               WHERE transaction_id = $3""",
            req.chosen_slot, datetime.utcnow(), req.transaction_id
        )
        return {"status": "pickup_scheduled", "pickup_time": req.chosen_slot}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 4 → Dealer confirms pickup + condition
#  Status: pickup_scheduled → awaiting_seller_payment_confirm
# ─────────────────────────────────────────────

@router.post("/pickup/confirm")
async def confirm_pickup(req: PickupConfirmRequest):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", req.transaction_id
        )
        if not row or row["dealer_id"] != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if req.as_described:
            new_status = "awaiting_seller_payment_confirm"
        else:
            new_status = "dispute_flagged"

        await db.execute(
            """UPDATE transactions
               SET pickup_confirmed = TRUE,
                   pickup_confirmed_at = $1,
                   vehicle_as_described = $2,
                   discrepancy_note = $3,
                   status = $4
               WHERE transaction_id = $5""",
            datetime.utcnow(), req.as_described,
            req.discrepancy_note, new_status, req.transaction_id
        )
        return {"status": new_status}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 5 → Seller confirms they received payment
#  Status: awaiting_seller_payment_confirm → awaiting_seller_fee
# ─────────────────────────────────────────────

@router.post("/seller/confirm-payment-received")
async def seller_confirm_payment(req: SellerPaymentConfirmRequest):
    db = await get_db()
    try:
        row = await db.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", req.transaction_id
        )
        if not row or row["seller_id"] != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        await db.execute(
            """UPDATE transactions
               SET seller_payment_confirmed = TRUE,
                   seller_payment_confirmed_at = $1,
                   status = 'awaiting_seller_fee'
               WHERE transaction_id = $2""",
            datetime.utcnow(), req.transaction_id
        )
        return {"status": "awaiting_seller_fee", "message": "Please pay the $250 PrivaBuy fee to complete."}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  STEP 6 → Seller pays $250 (called after Stripe)
#  Status: awaiting_seller_fee → completed
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/seller-paid")
async def mark_seller_paid(transaction_id: str):
    db = await get_db()
    try:
        await db.execute(
            """UPDATE transactions
               SET seller_fee_paid = TRUE,
                   seller_paid_at = $1,
                   status = 'completed',
                   completed_at = $1
               WHERE transaction_id = $2""",
            datetime.utcnow(), transaction_id
        )
        return {"status": "completed", "message": "Transaction complete. Congratulations!"}
    finally:
        await db.close()


# ─────────────────────────────────────────────
#  FORFEIT (admin or auto-triggered)
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/forfeit")
async def forfeit_transaction(transaction_id: str):
    db = await get_db()
    try:
        await db.execute(
            "UPDATE transactions SET status = 'forfeited', forfeited_at = $1 WHERE transaction_id = $2",
            datetime.utcnow(), transaction_id
        )
        return {"status": "forfeited"}
    finally:
        await db.close()