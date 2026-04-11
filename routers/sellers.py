from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from datetime import datetime
from app.database import get_connection


router = APIRouter(
    prefix="/sellers",
    tags=["sellers"]
)


class SellerCreate(BaseModel):
    phone: str
    email: str

@router.post("/register")
def register_seller(data: SellerCreate):
    conn = get_connection()
    cur = conn.cursor()

    seller_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO sellers (id, phone, email, created_at)
        VALUES (%s, %s, %s, %s)
    """, (
        seller_id,
        data.phone,
        data.email,
        datetime.utcnow()
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"seller_id": seller_id}