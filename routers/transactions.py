from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
from database import get_connection

router = APIRouter(prefix="/transactions", tags=["transactions"])

# ─────────────────────────────────────────────
#  MODELS
# ─────────────────────────────────────────────

class ProposeTimeSlotsRequest(BaseModel):
    transaction_id: str
    dealer_id: str
    slot_1: str
    slot_2: str
    slot_3: str

class ConfirmSlotRequest(BaseModel):
    transaction_id: str
    seller_id: str
    chosen_slot: str

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
#  INTERNAL HELPER — called from offers.py
# ─────────────────────────────────────────────

def create_transaction_record(cur, offer_id: str, car_id: str,
                               dealer_id: str, seller_id: str, amount: float):
    transaction_id = str(uuid.uuid4())
    deadline = datetime.utcnow() + timedelta(hours=24)
    cur.execute("""
        INSERT INTO transactions (
            transaction_id, offer_id, car_id, dealer_id, seller_id,
            amount, status, dealer_payment_deadline,
            dealer_fee_paid, seller_fee_paid,
            bill_of_sale_dealer_acked, bill_of_sale_seller_acked,
            created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        transaction_id, offer_id, car_id, dealer_id, seller_id,
        amount, "awaiting_dealer_payment", deadline,
        False, False, False, False,
        datetime.utcnow()
    ))
    return transaction_id


# ─────────────────────────────────────────────
#  GET by transaction_id
# ─────────────────────────────────────────────

@router.get("/car/{car_id}")
def get_transaction_by_car(car_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM transactions
            WHERE car_id = %s
            ORDER BY created_at DESC LIMIT 1
        """, (car_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="No transaction for this car")
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))
    finally:
        cur.close()
        conn.close()


@router.get("/dealer/{dealer_id}")
def get_dealer_transactions(dealer_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM transactions
            WHERE dealer_id = %s
            ORDER BY created_at DESC
        """, (dealer_id,))
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    finally:
        cur.close()
        conn.close()


@router.get("/seller/{seller_id}")
def get_seller_transactions(seller_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM transactions
            WHERE seller_id = %s
            ORDER BY created_at DESC
        """, (seller_id,))
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    finally:
        cur.close()
        conn.close()


@router.get("/{transaction_id}")
def get_transaction(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT * FROM transactions
            WHERE transaction_id = %s
        """, (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 1 — Dealer pays $600
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/dealer-paid")
def mark_dealer_paid(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT status, dealer_payment_deadline FROM transactions WHERE transaction_id = %s",
            (transaction_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        status, deadline = row
        if datetime.utcnow() > deadline:
            cur.execute(
                "UPDATE transactions SET status = 'forfeited', forfeited_at = %s WHERE transaction_id = %s",
                (datetime.utcnow(), transaction_id)
            )
            conn.commit()
            raise HTTPException(status_code=400, detail="24hr deadline expired — bid forfeited")
        cur.execute("""
            UPDATE transactions
            SET dealer_fee_paid = TRUE, dealer_paid_at = %s, status = 'awaiting_bill_of_sale'
            WHERE transaction_id = %s
        """, (datetime.utcnow(), transaction_id))
        conn.commit()
        return {"status": "awaiting_bill_of_sale"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 2 — Bill of Sale acknowledgment
# ─────────────────────────────────────────────

@router.post("/bill-of-sale/acknowledge")
def acknowledge_bill_of_sale(req: BillOfSaleAckRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if req.party == "dealer":
            cur.execute("""
                UPDATE transactions SET bill_of_sale_dealer_acked = TRUE, dealer_acked_at = %s
                WHERE transaction_id = %s
            """, (datetime.utcnow(), req.transaction_id))
        elif req.party == "seller":
            cur.execute("""
                UPDATE transactions SET bill_of_sale_seller_acked = TRUE, seller_acked_at = %s
                WHERE transaction_id = %s
            """, (datetime.utcnow(), req.transaction_id))
        else:
            raise HTTPException(status_code=400, detail="party must be 'dealer' or 'seller'")

        cur.execute("""
            SELECT bill_of_sale_dealer_acked, bill_of_sale_seller_acked
            FROM transactions WHERE transaction_id = %s
        """, (req.transaction_id,))
        dealer_acked, seller_acked = cur.fetchone()

        if dealer_acked and seller_acked:
            cur.execute("""
                UPDATE transactions SET status = 'awaiting_pickup_schedule'
                WHERE transaction_id = %s
            """, (req.transaction_id,))
            conn.commit()
            return {"status": "awaiting_pickup_schedule", "both_acked": True}

        conn.commit()
        waiting_on = "seller" if req.party == "dealer" else "dealer"
        return {"status": "awaiting_bill_of_sale", "both_acked": False, "waiting_on": waiting_on}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 3a — Dealer proposes 3 pickup slots
# ─────────────────────────────────────────────

@router.post("/pickup/propose-slots")
def propose_pickup_slots(req: ProposeTimeSlotsRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT dealer_id FROM transactions WHERE transaction_id = %s",
            (req.transaction_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        cur.execute("""
            UPDATE transactions
            SET pickup_slot_1 = %s, pickup_slot_2 = %s, pickup_slot_3 = %s,
                slots_proposed_at = %s, status = 'awaiting_slot_confirmation'
            WHERE transaction_id = %s
        """, (req.slot_1, req.slot_2, req.slot_3, datetime.utcnow(), req.transaction_id))
        conn.commit()
        return {"status": "awaiting_slot_confirmation"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 3b — Seller picks a slot
# ─────────────────────────────────────────────

@router.post("/pickup/confirm-slot")
def confirm_pickup_slot(req: ConfirmSlotRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT seller_id FROM transactions WHERE transaction_id = %s",
            (req.transaction_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        cur.execute("""
            UPDATE transactions
            SET confirmed_pickup_slot = %s, slot_confirmed_at = %s, status = 'pickup_scheduled'
            WHERE transaction_id = %s
        """, (req.chosen_slot, datetime.utcnow(), req.transaction_id))
        conn.commit()
        return {"status": "pickup_scheduled", "pickup_time": req.chosen_slot}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 4 — Dealer confirms pickup
# ─────────────────────────────────────────────

@router.post("/pickup/confirm")
def confirm_pickup(req: PickupConfirmRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT dealer_id FROM transactions WHERE transaction_id = %s",
            (req.transaction_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        new_status = "awaiting_seller_payment_confirm" if req.as_described else "dispute_flagged"
        cur.execute("""
            UPDATE transactions
            SET pickup_confirmed = TRUE, pickup_confirmed_at = %s,
                vehicle_as_described = %s, discrepancy_note = %s, status = %s
            WHERE transaction_id = %s
        """, (datetime.utcnow(), req.as_described, req.discrepancy_note, new_status, req.transaction_id))
        conn.commit()
        return {"status": new_status}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 5 — Seller confirms payment received
# ─────────────────────────────────────────────

@router.post("/seller/confirm-payment-received")
def seller_confirm_payment(req: SellerPaymentConfirmRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT seller_id FROM transactions WHERE transaction_id = %s",
            (req.transaction_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        cur.execute("""
            UPDATE transactions
            SET seller_payment_confirmed = TRUE, seller_payment_confirmed_at = %s,
                status = 'awaiting_seller_fee'
            WHERE transaction_id = %s
        """, (datetime.utcnow(), req.transaction_id))
        conn.commit()
        return {"status": "awaiting_seller_fee"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  STEP 6 — Seller pays $250
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/seller-paid")
def mark_seller_paid(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE transactions
            SET seller_fee_paid = TRUE, seller_paid_at = %s,
                status = 'completed', completed_at = %s
            WHERE transaction_id = %s
        """, (datetime.utcnow(), datetime.utcnow(), transaction_id))
        conn.commit()
        return {"status": "completed"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  FORFEIT
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/forfeit")
def forfeit_transaction(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE transactions SET status = 'forfeited', forfeited_at = %s
            WHERE transaction_id = %s
        """, (datetime.utcnow(), transaction_id))
        conn.commit()
        return {"status": "forfeited"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()