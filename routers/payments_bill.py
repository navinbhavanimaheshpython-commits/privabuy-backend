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
        customer_id = result["id"]

        cur.execute(f"UPDATE {party_table} SET bill_customer_id = %s WHERE id = %s", (customer_id, party_id))
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

async def create_invoice_for_transaction(transaction_id: str, party_id: str, amount: float, fee_type: str):
    """
    party_id is the dealer_id when fee_type == 'dealer_fee', or the seller_id when fee_type == 'seller_fee'.
    Bills the correct party — this replaces the old create_dealer_invoice, which always billed the dealer.
    """
    if fee_type not in FEE_DESCRIPTIONS:
        raise HTTPException(status_code=400, detail=f"Invalid fee_type: {fee_type}")

    conn = get_connection()
    try:
        cur = conn.cursor()

        if fee_type == "dealer_fee":
            cur.execute("""
                SELECT t.amount, t.car_id,
                       d.dealer_name, d.email
                FROM transactions t
                JOIN dealers d ON d.id = t.dealer_id::uuid
                WHERE t.transaction_id = %s
            """, (transaction_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Transaction not found")
            win_price, car_id, party_name, party_email = row
            party_table = "dealers"
        else:  # seller_fee
            cur.execute("""
                SELECT t.amount, t.car_id,
                       s.name, s.email
                FROM transactions t
                JOIN sellers s ON s.id = t.seller_id::uuid
                WHERE t.transaction_id = %s
            """, (transaction_id,))
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Transaction not found")
            win_price, car_id, party_name, party_email = row
            party_table = "sellers"
            party_name = party_name or party_email  # sellers.name can be blank

        if not party_email:
            raise HTTPException(status_code=422, detail=f"{party_table[:-1].capitalize()} has no email on file")

        cur.execute("SELECT year, make, model FROM cars WHERE car_id = %s", (car_id,))
        car_row = cur.fetchone()
        vehicle = f"{car_row[0]} {car_row[1]} {car_row[2]}" if car_row else "Vehicle"

        cur.execute(
            "SELECT invoice_number, pay_url FROM invoices WHERE transaction_id = %s AND fee_type = %s",
            (transaction_id, fee_type),
        )
        existing = cur.fetchone()
        if existing:
            return {"invoice_number": existing[0], "pay_url": existing[1], "already_sent": True}

        customer_id = await get_or_create_bill_customer(party_table, party_id, party_name, party_email)

        invoice_number = generate_invoice_number(conn)
        description = f"{FEE_DESCRIPTIONS[fee_type]} — {vehicle}"

        bill_invoice = await bill_request("POST", "/invoices", {
            "customerId": customer_id,
            "invoiceNumber": invoice_number,
            "invoiceDate": datetime.now().strftime("%Y-%m-%d"),
            "dueDate": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
            "invoiceLineItems": [{
                "amount": amount,
                "description": description,
            }],
            "sendEmail": True,
        })

        pay_url = bill_invoice.get("payUrl") or bill_invoice.get("payLink", "")
        bill_invoice_id = bill_invoice["id"]

        cur.execute("""
            INSERT INTO invoices (invoice_number, transaction_id, dealer_id, dealer_email,
                                  dealer_name, vehicle, win_price, amount, bill_invoice_id,
                                  pay_url, status, fee_type)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (invoice_number, transaction_id, party_id if party_table == "dealers" else None, party_email,
              party_name, vehicle, float(win_price), amount, bill_invoice_id,
              pay_url, "sent", fee_type))
        conn.commit()

        return {
            "invoice_number": invoice_number,
            "pay_url": pay_url,
            "bill_invoice_id": bill_invoice_id,
            "party_email": party_email,
            "fee_type": fee_type,
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
                row = cur.fetchone()
                if row:
                    transaction_id, fee_type = row
                    cur.execute("UPDATE invoices SET status = 'paid' WHERE bill_invoice_id = %s", (bill_invoice_id,))

                    if fee_type == "seller_fee":
                        cur.execute("""
                            UPDATE transactions SET seller_fee_paid = TRUE, seller_paid_at = %s,
                            status = 'completed', completed_at = %s WHERE transaction_id = %s
                        """, (datetime.utcnow(), datetime.utcnow(), transaction_id))
                    elif fee_type == "dealer_fee":
                        cur.execute("""
                            UPDATE transactions SET dealer_fee_paid = TRUE, dealer_paid_at = %s,
                            status = 'awaiting_bill_of_sale' WHERE transaction_id = %s
                        """, (datetime.utcnow(), transaction_id))

                    conn.commit()
            finally:
                cur.close()
                conn.close()

    return {"ok": True} 