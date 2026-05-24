from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import uuid
from database import get_connection
import httpx
import os

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = "PrivaBuy <notifications@privabuy.com>"

def send_email_sync(to: str, subject: str, html: str):
    try:
        httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={"from": FROM_EMAIL, "to": [to], "subject": subject, "html": html},
            timeout=5
        )
    except Exception as e:
        print(f"Email failed: {e}")

def get_txn_parties(cur, transaction_id: str):
    cur.execute("""
        SELECT t.transaction_id, t.amount,
               c.year, c.make, c.model,
               s.email AS seller_email, s.name AS seller_name,
               d.email AS dealer_email, d.dealer_name
        FROM transactions t
        JOIN cars c ON c.car_id = t.car_id
        JOIN sellers s ON s.seller_id = t.seller_id
        JOIN dealers d ON d.dealer_id = t.dealer_id
        WHERE t.transaction_id = %s
    """, (transaction_id,))
    row = cur.fetchone()
    if not row:
        return None
    cols = [desc[0] for desc in cur.description]
    return dict(zip(cols, row))

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
    party: str


# ─────────────────────────────────────────────
#  INTERNAL HELPER
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
        cur.execute("SELECT * FROM transactions WHERE car_id = %s ORDER BY created_at DESC LIMIT 1", (car_id,))
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
        cur.execute("SELECT * FROM transactions WHERE dealer_id = %s ORDER BY created_at DESC", (dealer_id,))
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


# ─────────────────────────────────────────────
#  POST ROUTES
# ─────────────────────────────────────────────

@router.post("/bill-of-sale/acknowledge")
def acknowledge_bill_of_sale(req: BillOfSaleAckRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        if req.party == "dealer":
            cur.execute("UPDATE transactions SET bill_of_sale_dealer_acked = TRUE, dealer_acked_at = %s WHERE transaction_id = %s", (datetime.utcnow(), req.transaction_id))
        elif req.party == "seller":
            cur.execute("UPDATE transactions SET bill_of_sale_seller_acked = TRUE, seller_acked_at = %s WHERE transaction_id = %s", (datetime.utcnow(), req.transaction_id))
        else:
            raise HTTPException(status_code=400, detail="party must be 'dealer' or 'seller'")
        cur.execute("SELECT bill_of_sale_dealer_acked, bill_of_sale_seller_acked FROM transactions WHERE transaction_id = %s", (req.transaction_id,))
        dealer_acked, seller_acked = cur.fetchone()
        if dealer_acked and seller_acked:
            cur.execute("UPDATE transactions SET status = 'awaiting_pickup_schedule' WHERE transaction_id = %s", (req.transaction_id,))
            conn.commit()
            return {"status": "awaiting_pickup_schedule", "both_acked": True}
        conn.commit()
        p = get_txn_parties(cur, req.transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            if req.party == "dealer":
                send_email_sync(p['seller_email'], f"Please sign the Bill of Sale for your {vehicle}",
                    f"""<p>Hi {p['seller_name']},</p>
                    <p>The dealer has signed the Bill of Sale for your <strong>{vehicle}</strong>.</p>
                    <p>Please log in and sign your copy to move forward.</p>
                    <p style="margin-top:24px"><a href="https://privabuy.com/app?role=seller"
                       style="background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Sign Now →</a></p>""")
            elif req.party == "seller":
                send_email_sync(p['dealer_email'], f"Please sign the Bill of Sale for {vehicle}",
                    f"""<p>Hi {p['dealer_name']},</p>
                    <p>The seller has signed the Bill of Sale for the <strong>{vehicle}</strong>.</p>
                    <p>Please log in and sign your copy to move forward.</p>
                    <p style="margin-top:24px"><a href="https://privabuy.com/app?role=dealer"
                       style="background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Sign Now →</a></p>""")
        waiting_on = "seller" if req.party == "dealer" else "dealer"
        return {"status": "awaiting_bill_of_sale", "both_acked": False, "waiting_on": waiting_on}
    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@router.post("/pickup/propose-slots")
def propose_pickup_slots(req: ProposeTimeSlotsRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT dealer_id FROM transactions WHERE transaction_id = %s", (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.dealer_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        cur.execute("UPDATE transactions SET pickup_slot_1=%s, pickup_slot_2=%s, pickup_slot_3=%s, slots_proposed_at=%s, status='awaiting_slot_confirmation' WHERE transaction_id=%s",
                    (req.slot_1, req.slot_2, req.slot_3, datetime.utcnow(), req.transaction_id))
        conn.commit()
        p = get_txn_parties(cur, req.transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            send_email_sync(p['seller_email'], f"Choose a pickup time for your {vehicle}",
                f"""<p>Hi {p['seller_name']},</p>
                <p>The dealer has proposed pickup times for your <strong>{vehicle}</strong>.</p>
                <p>Please log in and choose the time that works best for you.</p>
                <p style="margin-top:24px"><a href="https://privabuy.com/app?role=seller"
                   style="background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Choose a Time →</a></p>""")
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
        cur.execute("SELECT seller_id FROM transactions WHERE transaction_id = %s", (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        cur.execute("UPDATE transactions SET confirmed_pickup_slot=%s, slot_confirmed_at=%s, status='pickup_scheduled' WHERE transaction_id=%s",
                    (req.chosen_slot, datetime.utcnow(), req.transaction_id))
        conn.commit()
        p = get_txn_parties(cur, req.transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            send_email_sync(p['dealer_email'], f"Pickup confirmed — {vehicle}",
                f"""<p>Hi {p['dealer_name']},</p>
                <p>The seller confirmed a pickup time for the <strong>{vehicle}</strong>.</p>
                <p><strong>Pickup time:</strong> {req.chosen_slot}</p>
                <p>Please arrive on time with payment ready.</p>
                <p style="margin-top:24px"><a href="https://privabuy.com/app?role=dealer"
                   style="background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">View Deal Flow →</a></p>""")
            send_email_sync(p['seller_email'], f"Pickup scheduled — {vehicle}",
                f"""<p>Hi {p['seller_name']},</p>
                <p>Your pickup for the <strong>{vehicle}</strong> is confirmed for <strong>{req.chosen_slot}</strong>.</p>
                <p>Have the title and keys ready.</p>""")
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
        new_status = "awaiting_seller_payment_confirm" if req.as_described else "dispute_flagged"
        cur.execute("UPDATE transactions SET pickup_confirmed=TRUE, pickup_confirmed_at=%s, vehicle_as_described=%s, discrepancy_note=%s, status=%s WHERE transaction_id=%s",
                    (datetime.utcnow(), req.as_described, req.discrepancy_note, new_status, req.transaction_id))
        conn.commit()
        p = get_txn_parties(cur, req.transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            if req.as_described:
                send_email_sync(p['seller_email'], f"Dealer confirmed pickup — please confirm payment for your {vehicle}",
                    f"""<p>Hi {p['seller_name']},</p>
                    <p>The dealer confirmed the <strong>{vehicle}</strong> was as described.</p>
                    <p>Once you receive payment from the dealer, confirm it in your Deal Flow tab.</p>
                    <p style="margin-top:24px"><a href="https://privabuy.com/app?role=seller"
                       style="background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">Confirm Payment →</a></p>""")
            else:
                send_email_sync(p['seller_email'], f"⚠️ Discrepancy flagged on your {vehicle}",
                    f"""<p>Hi {p['seller_name']},</p>
                    <p>The dealer flagged a discrepancy on the <strong>{vehicle}</strong>.</p>
                    <p><strong>Note:</strong> {req.discrepancy_note or 'No details provided.'}</p>
                    <p>PrivaBuy support will reach out within 24 hours.</p>""")
        return {"status": new_status}
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
        cur.execute("SELECT seller_id FROM transactions WHERE transaction_id = %s", (req.transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if str(row[0]) != req.seller_id:
            raise HTTPException(status_code=403, detail="Not authorized")
        cur.execute("UPDATE transactions SET seller_payment_confirmed=TRUE, seller_payment_confirmed_at=%s, status='awaiting_seller_fee' WHERE transaction_id=%s",
                    (datetime.utcnow(), req.transaction_id))
        conn.commit()
        p = get_txn_parties(cur, req.transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            send_email_sync(p['dealer_email'], f"Seller confirmed payment — deal wrapping up for {vehicle}",
                f"""<p>Hi {p['dealer_name']},</p>
                <p>The seller confirmed they received your payment for the <strong>{vehicle}</strong>. 🎉</p>
                <p>The deal is in its final step. You're all set!</p>""")
        return {"status": "awaiting_seller_fee"}
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
        cur.execute("SELECT status, dealer_payment_deadline FROM transactions WHERE transaction_id = %s", (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        status, deadline = row
        if datetime.utcnow() > deadline:
            cur.execute("UPDATE transactions SET status='forfeited', forfeited_at=%s WHERE transaction_id=%s", (datetime.utcnow(), transaction_id))
            conn.commit()
            raise HTTPException(status_code=400, detail="24hr deadline expired — bid forfeited")
        cur.execute("UPDATE transactions SET dealer_fee_paid=TRUE, dealer_paid_at=%s, status='awaiting_bill_of_sale' WHERE transaction_id=%s", (datetime.utcnow(), transaction_id))
        conn.commit()
        p = get_txn_parties(cur, transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            send_email_sync(p['seller_email'], f"The dealer paid — review your Bill of Sale for your {vehicle}",
                f"""<p>Hi {p['seller_name']},</p>
                <p>The winning dealer has paid their $600 PrivaBuy fee for your <strong>{vehicle}</strong>.</p>
                <p>Next step: review and sign the <strong>Bill of Sale</strong> in your Deal Flow tab.</p>
                <p style="margin-top:24px"><a href="https://privabuy.com/app?role=seller"
                   style="background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;">View Deal Flow →</a></p>""")
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
        p = get_txn_parties(cur, transaction_id)
        if p:
            vehicle = f"{p['year']} {p['make']} {p['model']}"
            send_email_sync(p['seller_email'], f"🎉 Your deal is complete — {vehicle}",
                f"""<p>Hi {p['seller_name']},</p>
                <p>Your sale of the <strong>{vehicle}</strong> is fully complete. Thank you for using PrivaBuy!</p>""")
            send_email_sync(p['dealer_email'], f"🎉 Deal complete — {vehicle}",
                f"""<p>Hi {p['dealer_name']},</p>
                <p>The deal for the <strong>{vehicle}</strong> is fully complete. Enjoy the vehicle!</p>""")
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
        cur.execute("UPDATE transactions SET status='forfeited', forfeited_at=%s WHERE transaction_id=%s", (datetime.utcnow(), transaction_id))
        conn.commit()
        return {"status": "forfeited"}
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