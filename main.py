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
