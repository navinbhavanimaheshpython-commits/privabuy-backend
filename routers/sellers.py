from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from datetime import datetime
from database import get_connection


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


@router.get("/{seller_id}/listings")
def get_seller_listings(seller_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT c.id, c.year, c.make, c.model, c.mileage, c.status, c.created_at,
                   c.floor_price,
                   (SELECT COUNT(*) FROM offers o WHERE o.car_id = c.id) as bid_count,
                   (SELECT MAX(offer_amount) FROM offers o WHERE o.car_id = c.id) as top_bid
            FROM cars c
            WHERE c.seller_id = %s
            ORDER BY c.created_at DESC
        """, (seller_id,))
        rows = cur.fetchall()
        return [{"car_id": str(r[0]), "year": r[1], "make": r[2], "model": r[3],
                 "mileage": r[4], "status": r[5], "created_at": str(r[6]),
                 "floor_price": float(r[7]) if r[7] else 0,
                 "bid_count": r[8], "top_bid": float(r[9]) if r[9] else 0} for r in rows]
    finally:
        cur.close()
        conn.close()