from fastapi import APIRouter, Request, HTTPException
import os
import uuid
import secrets
import httpx
from datetime import datetime
from database import get_connection
from email_utils import send_seller_magic_link

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

META_VERIFY_TOKEN = os.environ.get("META_VERIFY_TOKEN")
META_PAGE_ACCESS_TOKEN = os.environ.get("META_PAGE_ACCESS_TOKEN")


@router.get("/meta-leads")
def verify_webhook(request: Request):
    """Meta's one-time verification handshake when you register the webhook URL."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == META_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/meta-leads")
async def receive_lead(request: Request):
    """Meta pushes this every time someone submits the Instant Form."""
    body = await request.json()

    try:
        entries = body.get("entry", [])
        for entry in entries:
            for change in entry.get("changes", []):
                leadgen_id = change["value"]["leadgen_id"]
                await process_lead(leadgen_id)
    except Exception as e:
        print(f"[receive_lead] {e}")

    return {"status": "ok"}  # Always 200 quickly — Meta retries on non-200/timeout


async def process_lead(leadgen_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Skip if we've already processed this lead (Meta can retry deliveries)
        cur.execute("SELECT id FROM pending_sellers WHERE meta_leadgen_id = %s", (leadgen_id,))
        if cur.fetchone():
            return

        # Pull the full lead data from Graph API
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://graph.facebook.com/v19.0/{leadgen_id}",
                params={
                    "access_token": META_PAGE_ACCESS_TOKEN,
                    "fields": "field_data"
                }
            )
        data = resp.json()
        field_data = {f["name"]: f["values"][0] for f in data.get("field_data", [])}

        name = field_data.get("full_name", "")
        phone = field_data.get("phone_number", "")
        email = field_data.get("email", "")
        ymm = field_data.get("year_make_model", "")
        mileage = field_data.get("mileage", "")
        condition = field_data.get("condition", "")

        # Rough split of Y/M/M — refine later in the wizard, this is just a starting point
        parts = ymm.split(" ", 2)
        year = parts[0] if len(parts) > 0 else ""
        make = parts[1] if len(parts) > 1 else ""
        model = parts[2] if len(parts) > 2 else ""

        pending_id = str(uuid.uuid4())
        token = secrets.token_urlsafe(32)

        cur.execute("""
            INSERT INTO pending_sellers
                (id, name, phone, email, year, make, model, mileage, condition,
                 prefill_token, meta_leadgen_id, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (pending_id, name, phone, email, year, make, model, mileage, condition,
              token, leadgen_id, datetime.utcnow()))
        conn.commit()

        send_seller_magic_link(email, name, token, year, make, model)

    except Exception as e:
        conn.rollback()
        print(f"[process_lead] {e}")
    finally:
        cur.close()
        conn.close()