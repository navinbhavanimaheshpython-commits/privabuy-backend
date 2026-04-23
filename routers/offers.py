from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
import uuid
from datetime import datetime
import psycopg2
from typing import Literal


router = APIRouter(
    prefix="/offers",
    tags=["offers"]
)

class Offer(BaseModel):
    dealer_id: str
    car_id: str
    offer_amount: int


@router.post("/submit", status_code=201)
def submit_offer(data: Offer):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ Check dealer permission
        cur.execute("""
            SELECT 1
            FROM dealer_car_connections
            WHERE dealer_id = %s AND car_id = %s
        """, (data.dealer_id, data.car_id))

        if cur.fetchone() is None:
            raise HTTPException(
                status_code=403,
                detail="Dealer not authorized to bid on this car"
            )

        # 2️⃣ Check car is open
        cur.execute("""
            SELECT status FROM cars WHERE id = %s
        """, (data.car_id,))
        car = cur.fetchone()

        if not car or car[0] != "open":
            raise HTTPException(
                status_code=409,
                detail="Car is no longer accepting offers"
            )
            

        # 3️⃣ Insert offer
        offer_id = str(uuid.uuid4())

        cur.execute("""
            INSERT INTO offers (
                id, dealer_id, car_id, offer_amount, status, created_at
            )
            VALUES (%s, %s, %s, %s, 'pending', %s)
        """, (
            offer_id,
            data.dealer_id,
            data.car_id,
            data.offer_amount,
            datetime.utcnow()
        ))

        conn.commit()
        return {"status": "ok", "offer_id": offer_id}

    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail="Offer already submitted for this car"
        )
    
    except psycopg2.Error as e:
        conn.rollback()
        raise HTTPException(
            status_code=409,
            detail=str(e)
        )

    finally:
        cur.close()
        conn.close()
        

@router.get("/car/{car_id}/offers")
def list_offers(car_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, dealer_id, offer_amount, status, created_at
        FROM offers
        WHERE car_id = %s
    """, (car_id,))
    offers = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": o[0], "dealer_id": o[1], "offer_amount": o[2], "status": o[3], "created_at": o[4]} for o in offers]


class AcceptOffer(BaseModel):
    seller_id: str


# DO NOT MODIFY WITHOUT RE-RUNNING FEATURE E CONCURRENCY TESTS
# 🚨 CRITICAL SECTION — DO NOT MODIFY 🚨
# This function is concurrency-tested and guarantees:
# - exactly one accepted offer per car
# - all others rejected
# - no race conditions under concurrent requests
#
# ANY modification REQUIRES:
# 1. Re-running concurrency tests
# 2. Re-validating all invariants
#
# If you change this without testing, you WILL introduce race conditions.
@router.post("/accept/{offer_id}")
def accept_offer(offer_id: str, data: AcceptOffer):
    seller_id = data.seller_id
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ Get car_id from offer (no lock yet)
        cur.execute("""
            SELECT car_id
            FROM offers
            WHERE id = %s
        """, (offer_id,))
        result = cur.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Offer not found")

        car_id = result[0]

        # 2️⃣ LOCK CAR FIRST (this is the key fix)
        cur.execute("""
            SELECT seller_id, status
            FROM cars
            WHERE id = %s
            FOR UPDATE
        """, (car_id,))
        car = cur.fetchone()

        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        car_seller_id, car_status = car

        if car_status != "open":
            raise HTTPException(
                status_code=409,
                detail="Offers are closed for this vehicle"
            )

        if str(car_seller_id) != seller_id:
            raise HTTPException(
                status_code=403,
                detail="Not authorized to accept offers for this car"
            )

        # 3️⃣ LOCK TARGET OFFER
        cur.execute("""
            SELECT status
            FROM offers
            WHERE id = %s
            FOR UPDATE
        """, (offer_id,))
        offer = cur.fetchone()

        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")

        current_status = offer[0]

        if current_status != "pending":
            raise HTTPException(status_code=409, detail="Offer already processed")

        # 4️⃣ Check if any offer already accepted (NOW SAFE)
        cur.execute("""
            SELECT id
            FROM offers
            WHERE car_id = %s AND status = 'accepted'
        """, (car_id,))
        existing = cur.fetchone()

        if existing:
            raise HTTPException(
                status_code=409,
                detail="Another offer has already been accepted"
            )

        # 5️⃣ ACCEPT THIS OFFER
        cur.execute("""
            UPDATE offers
            SET status = 'accepted'
            WHERE id = %s
        """, (offer_id,))

        # 6️⃣ REJECT OTHERS
        cur.execute("""
            UPDATE offers
            SET status = 'rejected'
            WHERE car_id = %s
              AND id != %s
              AND status = 'pending'
        """, (car_id, offer_id))

        # 7️⃣ UPDATE CAR
        cur.execute("""
            UPDATE cars
            SET status = 'accepted_pending_settlement'
            WHERE id = %s
        """, (car_id,))

        conn.commit()
        return {"status": "ok", "accepted_offer": offer_id}

    except Exception as e:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()



# 🚨 CRITICAL SECTION — DO NOT MODIFY 🚨
# This function is concurrency-tested and guarantees:
# - exactly one accepted offer per car
# - all others rejected
# - no race conditions under concurrent requests
#
# ANY modification REQUIRES:
# 1. Re-running concurrency tests
# 2. Re-validating all invariants
#
# If you change this without testing, you WILL introduce race conditions.
class SettleOffer(BaseModel):
    result: Literal["success", "failure"]
    seller_id: str

@router.post("/settle/{offer_id}")
def settle_offer(offer_id: str, data: SettleOffer):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1️⃣ Lock offer
        cur.execute("""
            SELECT car_id, status
            FROM offers
            WHERE id = %s
            FOR UPDATE
        """, (offer_id,))
        offer = cur.fetchone()

        if not offer:
            raise HTTPException(404, "Offer not found")

        car_id, offer_status = offer

        # 2️⃣ Lock car
        cur.execute("""
            SELECT status, seller_id
            FROM cars
            WHERE id = %s
            FOR UPDATE
        """, (car_id,))
        car = cur.fetchone()

        if not car:
            raise HTTPException(404, "Car not found")

        car_status, car_seller_id = car

        if str(car_seller_id) != str(data.seller_id):
            raise HTTPException(status_code=403,detail="Not authourized to settle this car")


        # 3️⃣ PRECONDITIONS (non-negotiable)
        if offer_status != "accepted":
            raise HTTPException(
                status_code=409,
                detail="Offer not ready for settlement"
            )

        if car_status != "accepted_pending_settlement":
            raise HTTPException(
                status_code=409,
                detail="Car not ready for settlement"
            )

        # 4️⃣ TRANSITIONS
        if data.result == "success":
            cur.execute(
                "UPDATE cars SET status = 'settled' WHERE id = %s",
                (car_id,)
            )
        else: #failure
            cur.execute(
                "UPDATE offers SET status = 'settlement_failed' WHERE id = %s",
                (offer_id,)
            )
            cur.execute(
                "UPDATE cars SET status = 'open' WHERE id = %s",
                (car_id,)
            )

        conn.commit()
        return {"status": "ok"}
    
    except HTTPException as e:
        conn.rollback()
        raise

    except Exception as e:
        conn.rollback()
        raise HTTPException(500,detail=str(e))

    finally:
        cur.close()
        conn.close()

from typing import Literal

@router.get("/dealer/{dealer_id}/won")
def get_dealer_won_vehicles(dealer_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.id, o.car_id, o.offer_amount, o.created_at,
                   c.year, c.make, c.model, c.mileage, c.condition,
                   s.phone as seller_phone, s.email as seller_email
            FROM offers o
            JOIN cars c ON o.car_id = c.id
            JOIN sellers s ON c.seller_id = s.id
            WHERE o.dealer_id = %s AND o.status = 'accepted'
            ORDER BY o.created_at DESC
        """, (dealer_id,))
        rows = cur.fetchall()
        return [{"offer_id": str(r[0]), "car_id": str(r[1]), "amount": r[2],
                 "won_at": str(r[3]), "year": r[4], "make": r[5], "model": r[6],
                 "mileage": r[7], "condition": r[8],
                 "seller_phone": r[9], "seller_email": r[10]} for r in rows]
    finally:
        cur.close()
        conn.close()

@router.get("/dealer/{dealer_id}/analytics")
def get_dealer_analytics(dealer_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Total auctions entered
        cur.execute("""
            SELECT COUNT(*) FROM offers WHERE dealer_id = %s
        """, (dealer_id,))
        total_entered = cur.fetchone()[0]

        # Won
        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(offer_amount), 0)
            FROM offers WHERE dealer_id = %s AND status = 'accepted'
        """, (dealer_id,))
        won_row = cur.fetchone()
        total_won = won_row[0]
        total_spend = won_row[1]

        win_rate = round((total_won / total_entered * 100), 1) if total_entered > 0 else 0
        avg_price = round(total_spend / total_won) if total_won > 0 else 0

        return {
            "total_entered": total_entered,
            "total_won": total_won,
            "total_spend": total_spend,
            "win_rate": win_rate,
            "avg_price_per_unit": avg_price
        }
    finally:
        cur.close()
        conn.close()




@router.get("/car/{car_id}/top-bids")
def get_top_bids(car_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT o.id, o.dealer_id, o.offer_amount, o.created_at
            FROM offers o
            WHERE o.car_id = %s AND o.status = 'pending'
            ORDER BY o.offer_amount DESC
            LIMIT 10
        """, (car_id,))
        rows = cur.fetchall()
        return [{"offer_id": str(r[0]), "dealer_id": str(r[1]), 
                 "amount": r[2], "created_at": str(r[3])} for r in rows]
    finally:
        cur.close()
        conn.close()