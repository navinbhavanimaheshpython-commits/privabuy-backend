from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
from database import get_connection
from email_utils import (
    send_dealer_bid_accepted,
    send_seller_bid_accepted_confirmation,
    send_seller_dealer_paid_fee,
    send_dealer_seller_signed_bos,
    send_seller_dealer_signed_bos,
    send_seller_pickup_slots_proposed,
    send_dealer_pickup_confirmed,
    send_seller_pickup_confirmed,
    send_seller_vehicle_confirmed,
    send_deal_complete,
    send_admin_dispute_filed,
)


router = APIRouter(prefix="/transactions", tags=["transactions"])

# ─────────────────────────────────────────────
#  SLOT FORMATTER — used by pickup endpoints
# ─────────────────────────────────────────────

def fmt_slot(slot_str: str) -> str:
    try:
        return datetime.fromisoformat(slot_str).strftime("%A, %B %-d at %-I:%M %p")
    except Exception:
        return slot_str


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
    party: str


# ─────────────────────────────────────────────
#  INTERNAL HELPER
# ─────────────────────────────────────────────

def create_transaction_record(cur, offer_id: str, car_id: str,
                               dealer_id: str, seller_id: str, amount: float):
    transaction_id = str(uuid.uuid4())
    deadline = datetime.utcnow() + timedelta(hours=24)
    cur.execute("SELECT has_accident FROM cars WHERE car_id = %s", (car_id,))
    car_row = cur.fetchone()
    has_accident = bool(car_row[0]) if car_row and car_row[0] is not None else False
    cur.execute("""
        INSERT INTO transactions (
            transaction_id, offer_id, car_id, dealer_id, seller_id,
            amount, status, dealer_payment_deadline,
            dealer_fee_paid, seller_fee_paid,
            bill_of_sale_dealer_acked, bill_of_sale_seller_acked,
            has_accident, created_at
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        transaction_id, offer_id, car_id, dealer_id, seller_id,
        amount, "awaiting_dealer_payment", deadline,
        False, False, False, False,
        has_accident, datetime.utcnow()
    ))
    return transaction_id


# ─────────────────────────────────────────────
#  SPECIFIC GET ROUTES — must be above wildcard
# ─────────────────────────────────────────────

@router.get("/ping")
def ping():
    return {"status": "ok"}

@router.get("/car/{car_id}")
def get_transaction_by_car(car_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.*,
                   c.color, c.trim, c.mileage
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            WHERE t.car_id = %s
            ORDER BY t.created_at DESC LIMIT 1
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
            SELECT t.*,
                   c.year, c.make, c.model, c.color, c.trim, c.mileage
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            WHERE t.dealer_id = %s
            ORDER BY t.created_at DESC
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
        cur.execute("SELECT * FROM transactions WHERE seller_id = %s ORDER BY created_at DESC", (seller_id,))
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    finally:
        cur.close()
        conn.close()

@router.get("/ping/count")
def debug_count():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM transactions")
        count = cur.fetchone()[0]
        return {"table_exists": True, "row_count": count}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

@router.get("/admin/disputes")
def get_disputes():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.transaction_id, t.status, t.amount,
                   t.dispute_category, t.inspection_reject_reason,
                   t.dispute_evidence_urls, t.dispute_submitted_at,
                   t.inspection_rejected_at,
                   c.year, c.make, c.model
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            WHERE t.status = 'dispute_flagged'
            ORDER BY t.inspection_rejected_at DESC NULLS LAST
        """)
        rows = cur.fetchall()
        cols = [desc[0] for desc in cur.description]
        return [dict(zip(cols, r)) for r in rows]
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  POST ROUTES
# ─────────────────────────────────────────────

@router.post("/bill-of-sale/acknowledge")
def acknowledge_bill_of_sale(req: BillOfSaleAckRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if req.party == "dealer":
            cur.execute("""UPDATE transactions 
                SET bill_of_sale_dealer_acked=TRUE, dealer_acked_at=%s 
                WHERE transaction_id=%s""", (datetime.utcnow(), req.transaction_id))
        elif req.party == "seller":
            cur.execute("""UPDATE transactions 
                SET bill_of_sale_seller_acked=TRUE, seller_acked_at=%s 
                WHERE transaction_id=%s""", (datetime.utcnow(), req.transaction_id))
        else:
            raise HTTPException(status_code=400, detail="party must be 'dealer' or 'seller'")

        # Re-read both flags after writing — prevents race condition
        cur.execute("""
            SELECT t.bill_of_sale_dealer_acked, t.bill_of_sale_seller_acked,
                   t.car_id, t.dealer_id, t.seller_id,
                   c.year, c.make, c.model
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            WHERE t.transaction_id = %s
        """, (req.transaction_id,))
        row = cur.fetchone()
        dealer_acked, seller_acked, car_id, dealer_id, seller_id, year, make, model = row

        # Fetch emails for notifications
        cur.execute("SELECT email, dealer_name FROM dealers WHERE id = %s", (dealer_id,))
        d = cur.fetchone()
        dealer_email, dealer_name = (d[0], d[1]) if d else ("", "Dealer")

        cur.execute("SELECT email, name FROM sellers WHERE id = %s", (seller_id,))
        s = cur.fetchone()
        seller_email, seller_name = (s[0], s[1]) if s else ("", "Seller")

        if dealer_acked and seller_acked:
            # Guard: only advance if still at bill_of_sale stage
            cur.execute("""UPDATE transactions 
                SET status='awaiting_pickup_schedule'
                WHERE transaction_id=%s AND status='awaiting_bill_of_sale'""",
                (req.transaction_id,))
            conn.commit()

            # Both signed — notify dealer to propose slots
            send_seller_dealer_signed_bos(
                seller_email=seller_email, seller_name=seller_name,
                year=year, make=make, model=model
            )
            return {"status": "awaiting_pickup_schedule", "both_acked": True}

        conn.commit()
        waiting_on = "seller" if req.party == "dealer" else "dealer"

        # One party signed — notify the other
        if req.party == "dealer":
            # Dealer just signed → notify seller to sign
            send_dealer_seller_signed_bos(
                seller_email=seller_email, seller_name=seller_name,
                year=year, make=make, model=model
            )
        else:
            # Seller just signed → notify dealer to sign
            send_dealer_seller_signed_bos(
                dealer_email=dealer_email, dealer_name=dealer_name,
                year=year, make=make, model=model
            )

        return {"status": "awaiting_bill_of_sale", "both_acked": False, "waiting_on": waiting_on}
    except Exception as e:
        conn.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.post("/pickup/propose-slots")
def propose_pickup_slots(req: ProposeTimeSlotsRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.dealer_id, t.seller_id, c.year, c.make, c.model,
                   s.email, s.name
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            LEFT JOIN sellers s ON s.id::text = t.seller_id::text
            WHERE t.transaction_id = %s
        """, (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        dealer_id, seller_id, year, make, model, seller_email, seller_name = row
        if str(dealer_id) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        cur.execute("""UPDATE transactions 
            SET pickup_slot_1=%s, pickup_slot_2=%s, pickup_slot_3=%s,
                slots_proposed_at=%s, status='awaiting_slot_confirmation'
            WHERE transaction_id=%s""",
            (req.slot_1, req.slot_2, req.slot_3, datetime.utcnow(), req.transaction_id))
        conn.commit()

        # Notify seller to choose a time
        send_seller_pickup_slots_proposed(
            seller_email=seller_email or "",
            seller_name=seller_name or "Seller",
            year=year, make=make, model=model,
            slot_1=fmt_slot(req.slot_1),
            slot_2=fmt_slot(req.slot_2),
            slot_3=fmt_slot(req.slot_3),
        )

        return {"status": "awaiting_slot_confirmation"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/pickup/confirm-slot")
def confirm_pickup_slot(req: ConfirmSlotRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.seller_id, t.dealer_id, c.year, c.make, c.model,
                   s.email, s.name,
                   d.email, d.dealer_name
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            LEFT JOIN sellers s ON s.id::text = t.seller_id::text
            LEFT JOIN dealers d ON d.id::text = t.dealer_id::text
            WHERE t.transaction_id = %s
        """, (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        seller_id, dealer_id, year, make, model, seller_email, seller_name, dealer_email, dealer_name = row
        if str(seller_id) != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        cur.execute("""UPDATE transactions 
            SET confirmed_pickup_slot=%s, slot_confirmed_at=%s, status='pickup_scheduled'
            WHERE transaction_id=%s""",
            (req.chosen_slot, datetime.utcnow(), req.transaction_id))
        conn.commit()

        pickup_formatted = fmt_slot(req.chosen_slot)

        # Notify both parties of confirmed pickup time
        send_dealer_pickup_confirmed(
            dealer_email=dealer_email or "",
            dealer_name=dealer_name or "Dealer",
            year=year, make=make, model=model,
            pickup_time=pickup_formatted,
        )
        send_seller_pickup_confirmed(
            seller_email=seller_email or "",
            seller_name=seller_name or "Seller",
            year=year, make=make, model=model,
            pickup_time=pickup_formatted,
        )

        return {"status": "pickup_scheduled", "pickup_time": req.chosen_slot}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/pickup/confirm")
def confirm_pickup(req: PickupConfirmRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT dealer_id FROM transactions WHERE transaction_id = %s", (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        if req.as_described:
            inspection_deadline = datetime.utcnow() + timedelta(hours=24)
            cur.execute("""UPDATE transactions SET pickup_confirmed=TRUE, pickup_confirmed_at=%s,
                vehicle_as_described=TRUE, status='inspection_period',
                inspection_deadline=%s WHERE transaction_id=%s""",
                (datetime.utcnow(), inspection_deadline, req.transaction_id))
            conn.commit()
            return {"status": "inspection_period", "inspection_deadline": inspection_deadline.isoformat()}
        else:
            cur.execute("""UPDATE transactions SET pickup_confirmed=TRUE, pickup_confirmed_at=%s,
                vehicle_as_described=FALSE, discrepancy_note=%s, status='dispute_flagged'
                WHERE transaction_id=%s""",
                (datetime.utcnow(), req.discrepancy_note, req.transaction_id))
            conn.commit()
            return {"status": "dispute_flagged"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/seller/confirm-payment-received")
def seller_confirm_payment(req: SellerPaymentConfirmRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.seller_id, t.dealer_id, t.amount,
                   c.year, c.make, c.model,
                   s.email, s.name,
                   d.email, d.dealer_name
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            LEFT JOIN sellers s ON s.id::text = t.seller_id::text
            LEFT JOIN dealers d ON d.id::text = t.dealer_id::text
            WHERE t.transaction_id = %s
        """, (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        seller_id, dealer_id, amount, year, make, model, seller_email, seller_name, dealer_email, dealer_name = row
        if str(seller_id) != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        cur.execute("""UPDATE transactions 
            SET seller_payment_confirmed=TRUE, seller_payment_confirmed_at=%s,
                status='completed', completed_at=%s
            WHERE transaction_id=%s""",
            (datetime.utcnow(), datetime.utcnow(), req.transaction_id))
        conn.commit()

        # Notify both parties deal is done
        send_deal_complete(
            seller_email=seller_email or "",
            seller_name=seller_name or "Seller",
            dealer_email=dealer_email or "",
            dealer_name=dealer_name or "Dealer",
            year=year, make=make, model=model,
            amount=float(amount),
        )

        return {"status": "completed"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


class InspectionRejectRequest(BaseModel):
    dealer_id: str
    reason: str
    category: Optional[str] = None
    evidence_urls: Optional[list] = None


class InspectionAcceptRequest(BaseModel):
    dealer_id: str


@router.post("/{transaction_id}/inspection/accept")
def inspection_accept(transaction_id: str, req: InspectionAcceptRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.dealer_id, t.seller_id, t.amount, t.inspection_deadline,
                   c.year, c.make, c.model,
                   s.email, s.name
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            LEFT JOIN sellers s ON s.id::text = t.seller_id::text
            WHERE t.transaction_id = %s
        """, (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        dealer_id, seller_id, amount, inspection_deadline, year, make, model, seller_email, seller_name = row
        if str(dealer_id) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        cur.execute("""UPDATE transactions 
            SET status='awaiting_seller_payment_confirm', inspection_accepted_at=%s
            WHERE transaction_id=%s""",
            (datetime.utcnow(), transaction_id))
        conn.commit()

        # Notify seller to confirm payment
        send_seller_vehicle_confirmed(
            seller_email=seller_email or "",
            seller_name=seller_name or "Seller",
            year=year, make=make, model=model,
            amount=float(amount),
        )

        return {"status": "awaiting_seller_payment_confirm"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/{transaction_id}/inspection/reject")
def inspection_reject(transaction_id: str, req: InspectionRejectRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.dealer_id, t.seller_id, t.status,
                   c.year, c.make, c.model,
                   d.email, s.email
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            LEFT JOIN dealers d ON d.id::text = t.dealer_id::text
            LEFT JOIN sellers s ON s.id::text = t.seller_id::text
            WHERE t.transaction_id = %s
        """, (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        dealer_id, seller_id, pre_dispute_status, year, make, model, dealer_email, seller_email = row
        if str(dealer_id) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")

        cur.execute("""UPDATE transactions SET
            status='dispute_flagged',
            pre_dispute_status=%s,
            inspection_reject_reason=%s,
            inspection_rejected_at=%s,
            dispute_category=%s,
            dispute_evidence_urls=%s,
            dispute_submitted_at=%s
            WHERE transaction_id=%s""",
            (pre_dispute_status, req.reason, datetime.utcnow(),
             req.category, req.evidence_urls, datetime.utcnow(), transaction_id))
        conn.commit()

        # Notify admin of dispute
        send_admin_dispute_filed(
            txn_id=transaction_id,
            year=year, make=make, model=model,
            dealer_email=dealer_email or "",
            seller_email=seller_email or "",
        )

        return {"status": "dispute_flagged", "reason": req.reason}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


class DisputeResolveRequest(BaseModel):
    decision: str  # 'refund' or 'deny'


@router.post("/{transaction_id}/dispute/resolve")
def resolve_dispute(transaction_id: str, req: DisputeResolveRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT pre_dispute_status FROM transactions WHERE transaction_id = %s",
            (transaction_id,)
        )
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")

        pre_dispute_status = row[0] or "awaiting_dealer_payment"

        if req.decision == "refund":
            cur.execute(
                "UPDATE transactions SET status='dispute_resolved_refund', resolved_at=%s WHERE transaction_id=%s",
                (datetime.utcnow(), transaction_id)
            )
            new_status = "dispute_resolved_refund"
        else:
            cur.execute(
                """UPDATE transactions SET
                    status='dispute_resolved_denied',
                    resume_status=%s,
                    resolved_at=%s
                WHERE transaction_id=%s""",
                (pre_dispute_status, datetime.utcnow(), transaction_id)
            )
            new_status = "dispute_resolved_denied"

        conn.commit()
        return {"status": new_status, "decision": req.decision, "resumed_at": pre_dispute_status}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  WILDCARD POST ROUTES
# ─────────────────────────────────────────────

@router.post("/{transaction_id}/dealer-paid")
def mark_dealer_paid(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT t.status, t.dealer_payment_deadline, t.seller_id,
                   c.year, c.make, c.model,
                   s.email, s.name
            FROM transactions t
            LEFT JOIN cars c ON c.car_id::text = t.car_id::text
            LEFT JOIN sellers s ON s.id::text = t.seller_id::text
            WHERE t.transaction_id = %s
        """, (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        status, deadline, seller_id, year, make, model, seller_email, seller_name = row

        if deadline and datetime.utcnow() > deadline:
            cur.execute("UPDATE transactions SET status='forfeited', forfeited_at=%s WHERE transaction_id=%s",
                        (datetime.utcnow(), transaction_id))
            conn.commit()
            raise HTTPException(status_code=400, detail="24hr deadline expired — bid forfeited")

        cur.execute("""UPDATE transactions SET 
            dealer_fee_paid=TRUE, dealer_paid_at=%s, status='awaiting_bill_of_sale',
            bill_of_sale_dealer_acked=FALSE, bill_of_sale_seller_acked=FALSE
            WHERE transaction_id=%s""", (datetime.utcnow(), transaction_id))
        conn.commit()

        # Notify seller to sign Bill of Sale
        send_seller_dealer_paid_fee(
            seller_email=seller_email or "",
            seller_name=seller_name or "Seller",
            year=year, make=make, model=model,
        )

        return {"status": "awaiting_bill_of_sale"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/{transaction_id}/seller-paid")
def mark_seller_paid(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE transactions SET seller_fee_paid=TRUE, seller_paid_at=%s, status='completed', completed_at=%s WHERE transaction_id=%s",
                    (datetime.utcnow(), datetime.utcnow(), transaction_id))
        conn.commit()
        return {"status": "completed"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/{transaction_id}/forfeit")
def forfeit_transaction(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE transactions SET status='forfeited', forfeited_at=%s WHERE transaction_id=%s",
                    (datetime.utcnow(), transaction_id))
        conn.commit()
        return {"status": "forfeited"}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@router.post("/admin/repair-stuck/{transaction_id}")
def repair_stuck_transaction(transaction_id: str):
    """Auto-advance any transaction where both parties have signed but status didn't advance."""
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""SELECT status, bill_of_sale_dealer_acked, bill_of_sale_seller_acked 
                       FROM transactions WHERE transaction_id=%s""", (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(404, "Transaction not found")
        status, d_acked, s_acked = row
        if status == 'awaiting_bill_of_sale' and d_acked and s_acked:
            cur.execute("""UPDATE transactions SET status='awaiting_pickup_schedule' 
                           WHERE transaction_id=%s""", (transaction_id,))
            conn.commit()
            return {"repaired": True, "new_status": "awaiting_pickup_schedule"}
        return {"repaired": False, "status": status, "dealer_acked": d_acked, "seller_acked": s_acked}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


# ─────────────────────────────────────────────
#  WILDCARD GET — must be absolute last
# ─────────────────────────────────────────────

@router.get("/{transaction_id}")
def get_transaction(transaction_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM transactions WHERE transaction_id = %s", (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))
    finally:
        cur.close()
        conn.close()