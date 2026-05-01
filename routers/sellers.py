from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime
from database import get_connection
import hashlib

router = APIRouter(prefix="/sellers", tags=["sellers"])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

class SellerCreate(BaseModel):
    phone: str
    email: str
    password: str
    name: str = ''

class SellerLogin(BaseModel):
    email: str
    password: str

@router.post("/register")
def register_seller(data: SellerCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM sellers WHERE email = %s", (data.email,))
        existing = cur.fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered. Please log in instead.")
        seller_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO sellers (id, phone, email, password, name, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (seller_id, data.phone, data.email, hash_password(data.password), data.name, datetime.utcnow()))
        conn.commit()
        return {"seller_id": seller_id, "name": data.name, "email": data.email}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.post("/login")
def login_seller(data: SellerLogin):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name, password FROM sellers WHERE email = %s", (data.email,))
        seller = cur.fetchone()
        if not seller:
            raise HTTPException(status_code=404, detail="No account found with that email. Please register first.")
        seller_id, name, stored_password = seller
        if stored_password and stored_password != hash_password(data.password):
            raise HTTPException(status_code=401, detail="Incorrect password.")
        if not stored_password:
            cur.execute("UPDATE sellers SET password = %s WHERE id = %s", (hash_password(data.password), seller_id))
            conn.commit()
        return {"seller_id": str(seller_id), "name": name or data.email, "email": data.email}
    finally:
        cur.close()
        conn.close()

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