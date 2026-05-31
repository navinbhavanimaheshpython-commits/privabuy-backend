from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
import uuid
from datetime import datetime
import psycopg2
from typing import Literal
from email_utils import send_seller_new_bid

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
# TEMPORARILY DISABLED - auto-connect not yet implemented
# cur.execute("""
#     SELECT 1
#     FROM dealer_car_connections
#     WHERE dealer_id = %s AND car_id = %s
# """, (data.dealer_id, data.car_id))
# if cur.fetchone() is None:
#     raise HTTPException(
#         status_code=403,
#         detail="Dealer not authorized to bid on this car"
#     )

        # 2️⃣ Check car is open
        cur.execute("""
            SELECT status FROM cars WHERE car_id = %s
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

        # 4️⃣ Email seller about new bid
        cur.execute("""
            SELECT s.email, c.year, c.make, c.model
            FROM cars c JOIN sellers s ON c.seller_id = s.id
            WHERE c.car_id = %s
        """, (data.car_id,))
        car_info = cur.fetchone()
        if car_info:
            send_seller_new_bid(
                car_info[0], 'A dealer',
                data.offer_amount,
                car_info[1], car_info[2], car_info[3]
            )

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
        # 1 Get car_id from offer
        cur.execute("""
            SELECT car_id
            FROM offers
            WHERE id = %s
        """, (offer_id,))
        result = cur.fetchone()

        if not result:
            raise HTTPException(status_code=404, detail="Offer not found")

        car_id = result[0]

        # 2 LOCK CAR FIRST
        cur.execute("""
            SELECT seller_id, status
            FROM cars
            WHERE car_id = %s
            FOR UPDATE
        """, (car_id,))
        car = cur.fetchone()

        if not car:
            raise HTTPException(status_code=404, detail="Car not found")

        car_seller_id, car_status = car

        if car_status != "open":
            raise HTTPException(status_code=409, detail="Offers are closed for this vehicle")

        if str(car_seller_id) != seller_id:
            raise HTTPException(status_code=403, detail="Not authorized to accept offers for this car")

        # 3 LOCK TARGET OFFER
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

        # 4 Check if any offer already accepted
        cur.execute("""
            SELECT id
            FROM offers
            WHERE car_id = %s AND status = 'accepted'
        """, (car_id,))
        existing = cur.fetchone()

        if existing:
            raise HTTPException(status_code=409, detail="Another offer has already been accepted")

        # 5 ACCEPT THIS OFFER
        cur.execute("""
            UPDATE offers
            SET status = 'accepted'
            WHERE id = %s
        """, (offer_id,))

        # 6 REJECT OTHERS
        cur.execute("""
            UPDATE offers
            SET status = 'rejected'
            WHERE car_id = %s
              AND id != %s
              AND status = 'pending'
        """, (car_id, offer_id))

        # 7 UPDATE CAR
        cur.execute("""
            UPDATE cars
            SET status = 'accepted_pending_settlement'
            WHERE car_id = %s
        """, (car_id,))

        # 8 CREATE TRANSACTION RECORD
        from routers.transactions import create_transaction_record
        cur.execute("SELECT dealer_id, offer_amount FROM offers WHERE id = %s", (offer_id,))
        offer_row = cur.fetchone()
        create_transaction_record(
            cur=cur,
            offer_id=offer_id,
            car_id=car_id,
            dealer_id=str(offer_row[0]),
            seller_id=seller_id,
            amount=float(offer_row[1])
        )

        try:
            cur.execute("""
                SELECT c.year, c.make, c.model, s.email, s.name, d.email, d.dealer_name
                FROM cars c 
                JOIN sellers s ON c.seller_id = s.id
                JOIN dealers d ON d.id = %s
                WHERE c.car_id = %s
            """, (str(offer_row[0]), car_id))
            r = cur.fetchone()
            if r:
                from email_utils import send_dealer_bid_accepted, send_seller_bid_accepted_confirmation
                send_dealer_bid_accepted(r[5], r[6], r[0], r[1], r[2], float(offer_row[1]))
                send_seller_bid_accepted_confirmation(r[3], r[4] or 'Seller', r[0], r[1], r[2], float(offer_row[1]))
        except Exception as email_err:
            print(f"Email error: {email_err}")
            
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
            WHERE car_id = %s
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
            WHERE car_id = %s
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
                "UPDATE cars SET status = 'settled' WHERE car_id = %s",
                (car_id,)
            )
        else: #failure
            cur.execute(
                "UPDATE offers SET status = 'settlement_failed' WHERE car_id = %s",
                (offer_id,)
            )
            cur.execute(
                "UPDATE cars SET status = 'open' WHERE car_id = %s",
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
            JOIN cars c ON o.car_id = c.car_id
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
        cur.execute("SELECT COUNT(*) FROM offers WHERE dealer_id = %s", (dealer_id,))
        total_entered = cur.fetchone()[0]

        # Won
        cur.execute("""
            SELECT COUNT(*), COALESCE(SUM(offer_amount), 0)
            FROM offers WHERE dealer_id = %s AND status = 'accepted'
        """, (dealer_id,))
        won_row = cur.fetchone()
        total_won = won_row[0]
        total_spend = float(won_row[1])

        win_rate = round((total_won / total_entered * 100), 1) if total_entered > 0 else 0
        avg_price = round(total_spend / total_won) if total_won > 0 else 0

        # Bids per day last 30 days
        cur.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as bids
            FROM offers WHERE dealer_id = %s
            AND created_at > NOW() - INTERVAL '30 days'
            GROUP BY day ORDER BY day ASC
        """, (dealer_id,))
        bids_by_day = [{"date": str(r[0]), "bids": r[1]} for r in cur.fetchall()]

        # Top makes won
        cur.execute("""
            SELECT c.make, COUNT(*) as count
            FROM offers o JOIN cars c ON o.car_id = c.car_id
            WHERE o.dealer_id = %s AND o.status = 'accepted'
            GROUP BY c.make ORDER BY count DESC LIMIT 5
        """, (dealer_id,))
        top_makes = [{"make": r[0], "count": r[1]} for r in cur.fetchall()]

        # Avg bid vs winning bid on lost auctions
        cur.execute("""
            SELECT 
                AVG(o.offer_amount) as my_avg,
                AVG(winning.max_bid) as avg_winner
            FROM offers o
            JOIN (
                SELECT car_id, MAX(offer_amount) as max_bid
                FROM offers GROUP BY car_id
            ) winning ON o.car_id = winning.car_id
            WHERE o.dealer_id = %s AND o.status != 'accepted'
        """, (dealer_id,))
        bid_comp = cur.fetchone()
        my_avg_bid = round(float(bid_comp[0])) if bid_comp and bid_comp[0] else 0
        avg_winning_bid = round(float(bid_comp[1])) if bid_comp and bid_comp[1] else 0

        # Recent won vehicles
        cur.execute("""
            SELECT c.year, c.make, c.model, c.mileage, o.offer_amount, o.created_at
            FROM offers o JOIN cars c ON o.car_id = c.car_id
            WHERE o.dealer_id = %s AND o.status = 'accepted'
            ORDER BY o.created_at DESC LIMIT 5
        """, (dealer_id,))
        recent_won = [{"year": r[0], "make": r[1], "model": r[2], 
                       "mileage": r[3], "amount": float(r[4]), 
                       "date": str(r[5])} for r in cur.fetchall()]

        # This month vs last month spend
        cur.execute("""
            SELECT 
                COALESCE(SUM(CASE WHEN created_at > DATE_TRUNC('month', NOW()) THEN offer_amount ELSE 0 END), 0) as this_month,
                COALESCE(SUM(CASE WHEN created_at BETWEEN DATE_TRUNC('month', NOW()) - INTERVAL '1 month' AND DATE_TRUNC('month', NOW()) THEN offer_amount ELSE 0 END), 0) as last_month
            FROM offers WHERE dealer_id = %s AND status = 'accepted'
        """, (dealer_id,))
        months = cur.fetchone()
        this_month = float(months[0]) if months else 0
        last_month = float(months[1]) if months else 0

        return {
            "total_entered": total_entered,
            "total_won": total_won,
            "total_spend": total_spend,
            "win_rate": win_rate,
            "avg_price": avg_price,
            "bids_by_day": bids_by_day,
            "top_makes": top_makes,
            "my_avg_bid": my_avg_bid,
            "avg_winning_bid": avg_winning_bid,
            "recent_won": recent_won,
            "this_month_spend": this_month,
            "last_month_spend": last_month
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


@router.post("/expire-old")
def expire_old_listings():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE cars SET status = 'expired'
            WHERE status = 'open'
            AND created_at < NOW() - INTERVAL '30 days'
        """)
        conn.commit()
        return {"expired": cur.rowcount}
    finally:
        cur.close()
        conn.close()





################################working