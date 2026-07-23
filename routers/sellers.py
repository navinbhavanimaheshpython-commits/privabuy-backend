from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime, timedelta
import secrets
from database import get_connection
import hashlib
from email_utils import send_admin_new_seller, send_seller_welcome


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
        send_admin_new_seller(data.name, data.email, data.phone)
        send_seller_welcome(data.name, data.email)
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
            SELECT c.car_id, c.year, c.make, c.model, c.mileage, c.status, c.created_at,
                   c.floor_price,
                   (SELECT COUNT(*) FROM offers o WHERE o.car_id = c.car_id) as bid_count,
                   (SELECT MAX(offer_amount) FROM offers o WHERE o.car_id = c.car_id) as top_bid
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



import secrets
from datetime import timedelta

class ForgotPassword(BaseModel):
    email: str

class ResetPassword(BaseModel):
    token: str
    password: str

@router.post("/forgot-password")
def forgot_password(data: ForgotPassword):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id, name FROM sellers WHERE email = %s", (data.email,))
        seller = cur.fetchone()
        if not seller:
            return {"status": "ok"}  # Don't reveal if email exists
        token = secrets.token_urlsafe(32)
        expires = datetime.utcnow() + timedelta(hours=1)
        cur.execute("UPDATE sellers SET reset_token = %s, reset_token_expires = %s WHERE id = %s",
                    (token, expires, seller[0]))
        conn.commit()
        # Send reset email
        from email_utils import send_password_reset
        send_password_reset(data.email, seller[1] or data.email, token)
        return {"status": "ok"}
    finally:
        cur.close()
        conn.close()

@router.post("/reset-password")
def reset_password(data: ResetPassword):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id FROM sellers 
            WHERE reset_token = %s AND reset_token_expires > NOW()
        """, (data.token,))
        seller = cur.fetchone()
        if not seller:
            raise HTTPException(status_code=400, detail="Invalid or expired reset link.")
        cur.execute("""
            UPDATE sellers SET password = %s, reset_token = NULL, reset_token_expires = NULL
            WHERE id = %s
        """, (hash_password(data.password), seller[0]))
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()
        conn.close()


@router.get("/prefill/{token}")
def get_prefill_data(token: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT name, phone, email, year, make, model, mileage, condition
            FROM pending_sellers WHERE prefill_token = %s
        """, (token,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Invalid or expired link.")
        return {
            "name": row[0], "phone": row[1], "email": row[2],
            "year": row[3], "make": row[4], "model": row[5],
            "mileage": row[6], "condition": row[7]
        }
    finally:
        cur.close()
        conn.close()