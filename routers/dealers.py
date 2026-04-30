from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
import uuid
from datetime import datetime

router = APIRouter(prefix="/dealers", tags=["dealers"])

class DealerRegister(BaseModel):
    dealer_name: str
    contact_name: str
    phone: str
    email: str
    license_number: str
    city: str
    state: str

class DealerLogin(BaseModel):
    license_number: str
    email: str

@router.post("/register")
def dealer_register(data: DealerRegister):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM dealers WHERE license_number = %s", (data.license_number,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="License number already registered")
        dealer_id = str(uuid.uuid4())
        api_key = str(uuid.uuid4())[:12]
        cur.execute("""
            INSERT INTO dealers (id, dealer_name, contact_name, phone, email, license_number, city, state, api_key, status, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'approved',%s)
        """, (dealer_id, data.dealer_name, data.contact_name, data.phone,
              data.email, data.license_number, data.city, data.state, api_key, datetime.utcnow()))
        conn.commit()
        return {"status": "ok", "dealer_id": dealer_id, "api_key": api_key}
    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cur.close()
        conn.close()

@router.post("/login")
def dealer_login(data: DealerLogin):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, dealer_name, status FROM dealers
            WHERE license_number = %s AND email = %s
        """, (data.license_number, data.email))
        dealer = cur.fetchone()
        if not dealer:
            raise HTTPException(status_code=404, detail="No dealer found with that license number and email. Please register first.")
        dealer_id, dealer_name, status = dealer
        if status == 'pending':
            raise HTTPException(status_code=403, detail="Your account is pending approval.")
        if status == 'rejected':
            raise HTTPException(status_code=403, detail="Your account has been rejected. Contact support@privabuy.com.")
        return {"status": "ok", "dealer_id": str(dealer_id), "dealer_name": dealer_name}
    finally:
        cur.close()
        conn.close()

@router.get("/{dealer_id}/notifications")
def get_notifications(dealer_id: str):
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE dealer_notifications SET sent = true
            WHERE id IN (
              SELECT id FROM dealer_notifications
              WHERE dealer_id = %s AND sent = false
              ORDER BY created_at ASC
            )
            RETURNING id, car_id, type, created_at
        """, (dealer_id,))
        rows = cur.fetchall()
        return {"dealer_id": dealer_id, "dealer_notifications": [
            {"id": str(r[0]), "car_id": str(r[1]), "type": r[2], "created_at": str(r[3])}
            for r in rows
        ]}
    finally:
        cur.close()
        conn.close()




@router.get("/admin/all")
def admin_all_dealers():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, dealer_name, email, license_number, city, state, status, created_at
            FROM dealers ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        return [{"dealer_id": str(r[0]), "dealer_name": r[1], "email": r[2],
                 "license_number": r[3], "city": r[4], "state": r[5],
                 "status": r[6], "created_at": str(r[7])} for r in rows]
    finally:
        cur.close()
        conn.close()

@router.post("/{dealer_id}/approve")
def approve_dealer(dealer_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE dealers SET status = 'approved' WHERE id = %s", (dealer_id,))
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()
        conn.close()

@router.post("/{dealer_id}/reject")
def reject_dealer(dealer_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("UPDATE dealers SET status = 'rejected' WHERE id = %s", (dealer_id,))
        conn.commit()
        return {"status": "ok"}
    finally:
        cur.close()
        conn.close()



class LicenseCheck(BaseModel):
    license_number: str

@router.post("/check-license")
def check_license(data: LicenseCheck):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id FROM dealers WHERE license_number = %s", (data.license_number,))
        if cur.fetchone():
            raise HTTPException(status_code=409, detail="License already registered")
        return {"status": "available"}
    finally:
        cur.close()
        conn.close()