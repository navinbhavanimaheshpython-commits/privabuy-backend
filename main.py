from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import cars, dealers, offers, sellers, payments



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://privabuy.vercel.app", "http://localhost:5173", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cars.router)
app.include_router(dealers.router)
app.include_router(offers.router)
app.include_router(sellers.router)
app.include_router(payments.router)
@app.get("/")
def home():
    return {"message": "AutoOS API running"}


from fastapi import Header, HTTPException

ADMIN_PASSWORD = "Hanuman@1015"  # Change this
ADMIN_EMAIL = "navinbhavanimaheshpython@gmail.com"

@app.post("/admin/login")
def admin_login(data: dict):
    if data.get("email") != ADMIN_EMAIL or data.get("password") != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"status": "ok", "token": "pb-admin-2026"}