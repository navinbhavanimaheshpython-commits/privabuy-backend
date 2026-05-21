from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import cars, dealers, offers, sellers, payments, transactions

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