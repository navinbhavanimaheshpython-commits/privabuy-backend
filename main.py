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