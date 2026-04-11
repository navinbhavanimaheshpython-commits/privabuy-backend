from fastapi import APIRouter
from pydantic import BaseModel
from database import get_connection
import uuid
from datetime import datetime

router = APIRouter(
    prefix="/dealers",
    tags=["dealers"]
)

class DealerRegister(BaseModel):
    dealer_name: str
    contact_name: str
    phone: str
    email: str
    city: str
    state: str

@router.post("/register")
def dealer_register(data: DealerRegister):
    conn = get_connection()
    cur = conn.cursor()

    dealer_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())[:12]

    cur.execute("""
        INSERT INTO dealers (
            id, dealer_name, contact_name, phone,
            email, city, state, api_key, created_at
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        dealer_id,
        data.dealer_name,
        data.contact_name,
        data.phone,
        data.email,
        data.city,
        data.state,
        api_key,
        datetime.utcnow()
    ))


    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "dealer_id": dealer_id, "api_key": api_key}


@router.get("/{dealer_id}/notifications")
def get_notifications(dealer_id: str):
    conn = get_connection()
    conn.autocommit = True
    cur = conn.cursor()

    try:
        # 1. Fetch unsent notifications
        cur.execute("""
            SELECT id, car_id, type, created_at
            FROM dealer_notifications
            WHERE dealer_id = %s
              AND sent = false
            ORDER BY created_at ASC
        """, (dealer_id,))

        rows = cur.fetchall()

        # 2. Mark them as sent
        cur.execute("""
            UPDATE dealer_notifications
            SET sent = true
            WHERE id IN (
              SELECT id
              FROM dealer_notifications
            WHERE dealer_id = %s AND sent = false
           ORDER BY created_at ASC
         )
          RETURNING id, car_id, type, created_at
        """, (dealer_id,))

        conn.commit()
        
        rows = cur.fetchall()

        # 3. Format response
        return {
            "dealer_id": dealer_id,
            "dealer_notifications": [
                {
                    "id": str(r[0]),
                    "car_id": str(r[1]),
                    "type": r[2],
                    "created_at": str(r[3])
                }
                for r in rows
            ]
        }

    finally:
        cur.close()
        conn.close()
