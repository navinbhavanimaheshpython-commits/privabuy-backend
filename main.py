from fastapi import FastAPI
from routers import cars, dealers, offers, sellers
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

app.include_router(cars.router)
app.include_router(dealers.router)
app.include_router(offers.router)
app.include_router(sellers.router)

@app.get("/")
def home():
    return {"message": "AutoOS API running"}
