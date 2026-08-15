import hashlib
import hmac
import base64
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime, timedelta
import httpx
import os
from database import get_connection

router = APIRouter(prefix="/payments/bill", tags=["bill_payments"])

BILL_API_BASE = os.environ.get("BILL_API_BASE", "https://gateway.stage.bill.com/connect/v3")
BILL_DEV_KEY = os.environ["BILL_DEV_KEY"]
BILL_USERNAME = os.environ["BILL_USERNAME"]
BILL_PASSWORD = os.environ["BILL_PASSWORD"]
BILL_ORG_ID = os.environ["BILL_ORG_ID"]
BILL_WEBHOOK_SECURITY_KEY = os.environ["BILL_WEBHOOK_SECURITY_KEY"]

FEE_DESCRIPTIONS = {
    "seller_fee": "PrivaBuy Seller Fee",
    "dealer_fee": "PrivaBuy Dealer Platform Fee",
}

_session_cache = {"sessionId": None, "expires": None}


async def get_bill_session(force_refresh: bool = False) -> str:
    """Get a cached BILL session, logging in fresh if expired or forced."""
    if (
        not force_refresh
        and _session_cache["sessionId"]
        and _session_cache["expires"] > datetime.utcnow()
    ):
        return _session_cache["sessionId"]

    async with httpx.AsyncClient() as client:
        res = await client.post(
            f"{BILL_API_BASE}/login",
            json={
                "username": BILL_USERNAME,
                "password": BILL_PASSWORD,
                "organizationId": BILL_ORG_ID,
                "devKey": BILL_DEV_KEY,
            },
        )
        if res.status_code != 200:
            raise HTTPException(status_code=502, detail=f"BILL login failed: {res.text}")
        data = res.json()
        session_id = data["sessionId"]
        _session_cache["sessionId"] = session_id
        _session_cache["expires"] = datetime.utcnow() + timedelta(minutes=25)
        return session_id


async def bill_request(method: str, path: str, json_body: dict = None, _retried: bool = False):
    session_id = await get_bill_session()
    headers = {"devKey": BILL_DEV_KEY, "sessionId": session_id, "Content-Type": "application/json"}
    async with httpx.AsyncClient() as client:
        res = await client.request(method, f"{BILL_API_BASE}{path}", headers=headers, json=json_body)

        # Session may have been invalidated server-side even though our
        # local cache thought it was still valid. Retry once with a fresh login.
        if res.status_code == 401 and not _retried:
            await get_bill_session(force_refresh=True)
            return await bill_request(method, path, json_body, _retried=True)

        if res.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"BILL API error: {res.text}")
        return res.json()


async def get_or_create_bill_customer(party_table: str, party_id: str, party_name: str, party_email: str) -> str:
    """party_table must be 'dealers' or 'sellers'."""
    if party_table not in ("dealers", "sellers"):
        raise ValueError(f"Invalid party_table: {party_table}")

    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT bill_customer_id FROM {party_table} WHERE id = %s", (party_id,))
        row = cur.fetchone()
        if row and row[0]:
            return row[0]

        result = await bill_request("POST", "/customers", {
            "name": party_name,
            "email": party_email,
        })
        print(f"DEBUG: full customer creation response = {result!r}")  # temporary
        customer_id = result["id"]

        print(f"DEBUG: caching bill_customer_id={customer_id!r} for {party_table}.id={party_id!r}")  # temporary
        cur.execute(f"UPDATE {party_table} SET bill_customer_id = %s WHERE id = %s", (customer_id, party_id))
        print(f"DEBUG: rows updated = {cur.rowcount}")  # temporary
        conn.commit()
        return customer_id
    finally:
        cur.close()
        conn.close()


def generate_invoice_number(conn) -> str:
    year = datetime.now().year
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoices WHERE created_at >= date_trunc('year', NOW())")
    count = cur.fetchone()[0] + 1
    cur.close()
    return f"PB-{year}-{str(count).zfill(4)}"

SELLER_FEE = 350
DEALER_FEE = 450

async def create_combined_fee_invoice(transaction_id: str, dealer_id: str, include_dealer_fee: bool):
    """
    Bills the dealer, in a single BILL invoice, for the seller fee and
    (if applicable) the dealer platform fee. Fires once the seller confirms
    they've received payment for the car — the title-for-payment handoff —
    since that's the first point we know the deal is real. The dealer has
    already withheld the seller fee from what they paid the seller directly.
    """
    conn = get_connection()
    try:
        cur = conn.cursor()

        cur.execute("""
            SELECT t.amount, t.car_id, d.dealer_name, d.email
            FROM transactions t
            JOIN dealers d ON d.id = t.dealer_id::uuid
            WHERE t.transaction_id = %s
        """, (transaction_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
        win_price, car_id, dealer_name, dealer_email = row

        if not dealer_email:
            raise HTTPException(status_code=422, detail="Dealer has no email on file")

        cur.execute("SELECT year, make, model FROM cars WHERE car_id = %s", (car_id,))
        car_row = cur.fetchone()
        vehicle = f"{car_row[0]} {car_row[1]} {car_row[2]}" if car_row else "Vehicle"

        cur.execute(
            "SELECT invoice_number, pay_url FROM invoices WHERE transaction_id = %s AND fee_type = %s",
            (transaction_id, "seller_fee"),
        )
        existing = cur.fetchone()
        if existing:
            return {"invoice_number": existing[0], "pay_url": existing[1], "already_sent": True}

        line_items = [{
            "amount": SELLER_FEE,
            "quantity": 1,
            "description": (
                f"PrivaBuy Seller Fee — {vehicle} "
                f"(already withheld from your payment to the seller)"
            ),
        }]
        if include_dealer_fee:
            line_items.append({
                "amount": DEALER_FEE,
                "quantity": 1,
                "description": f"PrivaBuy Dealer Platform Fee — {vehicle}",
            })

        customer_id = await get_or_create_bill_customer("dealers", dealer_id, dealer_name, dealer_email)
        print(f"DEBUG: customer_id = {customer_id!r}")  # temporary
        invoice_number = generate_invoice_number(conn)

        bill_invoice = await bill_request("POST", "/invoices", {
            "customer": {"id": customer_id},
            "invoiceNumber": invoice_number,
            "invoiceDate": datetime.now().strftime("%Y-%m-%d"),
            "dueDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "invoiceLineItems": line_items,
            "processingOptions": {"sendEmail": False},  # TEMP: BDC_5217 — no bank account on BILL org yet. Flip to True after adding one.
        })

        pay_url = bill_invoice.get("payUrl") or bill_invoice.get("payLink", "")
        bill_invoice_id = bill_invoice["id"]

        cur.execute("""
            INSERT INTO invoices (invoice_number, transaction_id, dealer_id, dealer_email,
                                  dealer_name, vehicle, win_price, amount, bill_invoice_id,
                                  pay_url, status, fee_type)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (invoice_number, transaction_id, dealer_id, dealer_email,
              dealer_name, vehicle, float(win_price), SELLER_FEE, bill_invoice_id,
              pay_url, "sent", "seller_fee"))

        if include_dealer_fee:
            cur.execute("""
                INSERT INTO invoices (invoice_number, transaction_id, dealer_id, dealer_email,
                                      dealer_name, vehicle, win_price, amount, bill_invoice_id,
                                      pay_url, status, fee_type)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (invoice_number, transaction_id, dealer_id, dealer_email,
                  dealer_name, vehicle, float(win_price), DEALER_FEE, bill_invoice_id,
                  pay_url, "sent", "dealer_fee"))

        conn.commit()
        return {
            "invoice_number": invoice_number,
            "pay_url": pay_url,
            "bill_invoice_id": bill_invoice_id,
            "dealer_email": dealer_email,
            "seller_fee_amount": SELLER_FEE,
            "dealer_fee_amount": DEALER_FEE if include_dealer_fee else 0,
        }
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

        
def verify_bill_signature(raw_body: bytes, signature_header: str) -> bool:
    if not signature_header:
        return False
    computed = hmac.new(
        BILL_WEBHOOK_SECURITY_KEY.encode(), raw_body, hashlib.sha256
    ).digest()
    computed_b64 = base64.b64encode(computed).decode()
    return hmac.compare_digest(computed_b64, signature_header)


@router.post("/webhook")
async def bill_webhook(request: Request):
    raw_body = await request.body()
    signature = request.headers.get("x-bill-sha-signature", "")

    if not verify_bill_signature(raw_body, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    body = await request.json()

    # BILL's test/resend endpoints wrap the real payload as a JSON-escaped
    # string under "payload"; live webhook deliveries send it unwrapped.
    # Handle both so a sandbox test event doesn't silently no-op.
    if isinstance(body.get("payload"), str):
        import json
        payload = json.loads(body["payload"])
    else:
        payload = body

    event_type = payload.get("metadata", {}).get("eventType", "")

    # BILL has no invoice.paid / payment.completed event. Payment completion
    # arrives as invoice.updated with status flipped to PAID_IN_FULL.
    if event_type == "invoice.updated":
        invoice = payload.get("invoice", {})
        bill_invoice_id = invoice.get("id")
        status = invoice.get("status")

        if bill_invoice_id and status == "PAID_IN_FULL":
            conn = get_connection()
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT transaction_id, fee_type FROM invoices WHERE bill_invoice_id = %s",
                    (bill_invoice_id,),
                )
                rows = cur.fetchall()
                if rows:
                    transaction_id = rows[0][0]
                    fee_types = {r[1] for r in rows}
                    cur.execute("UPDATE invoices SET status = 'paid' WHERE bill_invoice_id = %s", (bill_invoice_id,))

                    if "dealer_fee" in fee_types:
                        cur.execute(
                            "UPDATE transactions SET dealer_fee_paid = TRUE, dealer_paid_at = %s WHERE transaction_id = %s",
                            (datetime.utcnow(), transaction_id)
                        )
                    if "seller_fee" in fee_types:
                        cur.execute("""
                            UPDATE transactions SET seller_fee_paid = TRUE, seller_paid_at = %s,
                            status = 'completed', completed_at = %s WHERE transaction_id = %s
                        """, (datetime.utcnow(), datetime.utcnow(), transaction_id))

                    conn.commit()
            finally:
                cur.close()
                conn.close()

    return {"ok": True} 