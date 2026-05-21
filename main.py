from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import cars, dealers, offers, sellers, payments, transactions

app = FastAPI()

origins = [
    "https://privabuy.com",
    "https://www.privabuy.com",
    "https://privabuy.vercel.app",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str, request: Request):
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
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