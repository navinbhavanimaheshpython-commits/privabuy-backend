from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from routers import cars, dealers, offers, sellers, payments, transactions, invoices, webhooks
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

app.include_router(cars.router)
app.include_router(dealers.router)
app.include_router(offers.router)
app.include_router(sellers.router)
app.include_router(payments.router)
app.include_router(transactions.router)
app.include_router(invoices.router, tags=["invoices"])
app.include_router(webhooks.router)

@app.get("/")
def home():
    return {"message": "AutoOS API running"}

ADMIN_PASSWORD = "Hanuman@1015"
ADMIN_EMAIL = "navinbhavanimaheshpython@gmail.com"

@app.post("/admin/login")
def admin_login(data: dict):
    if data.get("email") != ADMIN_EMAIL or data.get("password") != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "ok", "token": "pb-admin-2026"}


from fastapi.responses import JSONResponse

@app.post("/api/chat")
async def chat(request: Request):
    import httpx
    body = await request.json()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": os.environ["ANTHROPIC_API_KEY"],
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json=body,
            timeout=30
        )
    return JSONResponse(content=response.json())


from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from database import get_connection
import resend

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

def send_draft_nudges():
    if not RESEND_API_KEY:
        print("RESEND_API_KEY not set — skipping draft nudges")
        return
    conn = get_connection()
    cur = conn.cursor()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=1)
        cur.execute("""
            SELECT d.seller_id, d.year, d.make, d.model, s.email, s.name
            FROM car_drafts d
            JOIN sellers s ON s.id = d.seller_id::uuid
            WHERE d.completed = FALSE
            AND d.nudge_sent_at IS NULL
            AND d.updated_at <= %s
        """, (cutoff,))
        stale_drafts = cur.fetchall()

        for seller_id, year, make, model, email, name in stale_drafts:
            if not email:
                continue
            try:
                resend.Emails.send({
                    "from": "notifications@privabuy.com",
                    "to": email,
                    "subject": f"You're 80% done listing your {year} {make} {model}",
                    "html": f"""
                        <p>Hey {name or 'there'},</p>
                        <p>You started listing your <strong>{year} {make} {model}</strong>
                        on PrivaBuy — dealers are already checking new listings in your area.</p>
                        <p><a href="https://app.privabuy.com/seller?resume={seller_id}">
                        Finish your listing →</a></p>
                        <p>Takes about 2 more minutes.</p>
                    """,
                })
                cur.execute("UPDATE car_drafts SET nudge_sent_at = NOW() WHERE seller_id = %s", (seller_id,))
                conn.commit()
            except Exception as e:
                print(f"Resend nudge failed for seller {seller_id}: {e}")
    finally:
        cur.close()
        conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(send_draft_nudges, "interval", minutes=15)
scheduler.start()