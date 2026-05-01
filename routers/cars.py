from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from datetime import datetime
from database import get_connection
import json


router = APIRouter(
    prefix="/cars",
    tags=["cars"]
)

class CarListing(BaseModel):
    seller_id: str
    year: int
    make: str
    model: str
    mileage: int
    zip: str
    photos: list = []
    condition: str
    seller_phone: str
    seller_email: str
    vin: str = ''
    title_status: str = 'Clean'
    loan_status: str = 'None'
    trim: str = ''
    color: str = ''
    transmission: str = 'Automatic'
    drivetrain: str = 'FWD'
    keys: str = 'Yes'
    accidents: str = 'None'
    owners: int = 1
    smoked_in: bool = False
    overall_condition: str = ''
    comments: str = ''
    addons: str = ''

@router.post("/list-car")
def list_car(data: CarListing):
    conn = get_connection()
    cur = conn.cursor()
    try:
        car_id = str(uuid.uuid4())
        cur.execute("""
            INSERT INTO cars (id, seller_id, year, make, model, mileage, zip,
            condition, seller_phone, seller_email, created_at, status,
            vin, title_status, loan_status, trim, color, transmission,
            drivetrain, keys, accidents, owners, smoked_in, overall_condition,
            comments, addons, photos)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'open',
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            car_id, data.seller_id, data.year, data.make, data.model,
            data.mileage, data.zip, data.condition, data.seller_phone,
            data.seller_email, datetime.utcnow(),
            data.vin, data.title_status, data.loan_status, data.trim,
            data.color, data.transmission, data.drivetrain, data.keys,
            data.accidents, data.owners, data.smoked_in,
            data.overall_condition, data.comments, data.addons,
            json.dumps(data.photos)
        ))

        cur.execute("SELECT id FROM dealers ORDER BY created_at ASC LIMIT 5")
        dealers = cur.fetchall()
        for d in dealers:
            dealer_id = d[0]
            cur.execute("""
                INSERT INTO dealer_car_connections (id, car_id, dealer_id, created_at)
                VALUES (%s,%s,%s,%s)
            """, (str(uuid.uuid4()), car_id, dealer_id, datetime.utcnow()))
            cur.execute("""
                INSERT INTO dealer_notifications (id, dealer_id, car_id, type, created_at)
                VALUES (%s,%s,%s,%s,%s)
            """, (str(uuid.uuid4()), dealer_id, car_id, "NEW_CAR_ASSIGNED", datetime.utcnow()))

        conn.commit()
        return {"status": "ok", "car_id": car_id, "connected_dealers": len(dealers)}
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


@router.get("/active")
def get_active_cars():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, seller_id, year, make, model, mileage, zip, condition, created_at
            FROM cars WHERE status = 'open'
            ORDER BY created_at DESC
        """)
        cars = cur.fetchall()
        return [{"car_id": str(c[0]), "seller_id": str(c[1]), "year": c[2], "make": c[3], 
                 "model": c[4], "mileage": c[5], "zip": c[6], "condition": c[7],
                 "created_at": str(c[8])} for c in cars]
    finally:
        cur.close()
        conn.close()

@router.get("/market-value")
async def get_market_value(year: int, make: str, model: str, mileage: int):
    import httpx
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.get(
                "https://mc-api.marketcheck.com/v2/search/car/active",
                params={
                    "api_key": "odVSXlZhE7ioMdmA4HjBuVpLxttlY2JR",
                    "year": year,
                    "make": make.lower(),
                    "model": model.lower(),
                    "rows": 10,
                    "start": 0
                },
                headers={
                    "X-Api-Key": "odVSXlZhE7ioMdmA4HjBuVpLxttlY2JR"
                }
            )
            data = res.json()
            return {"raw": data, "status": res.status_code}
    except Exception as e:
        return {"error": str(e)}


@router.get("/admin/overview")
def admin_overview():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM cars WHERE status = 'open'")
        live = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM dealers WHERE status = 'approved'")
        dealers = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM cars WHERE created_at > NOW() - INTERVAL '30 days'")
        auctions_30d = cur.fetchone()[0]
        try:
            cur.execute("SELECT COALESCE(SUM(amount),0) FROM payments WHERE created_at > NOW() - INTERVAL '30 days'")
            revenue_30d = float(cur.fetchone()[0])
        except:
            revenue_30d = 0.0
        return {"live_auctions": live, "active_dealers": dealers, "auctions_30d": auctions_30d, "revenue_30d": revenue_30d}
    finally:
        cur.close()
        conn.close()


@router.get("/admin/listings")
def admin_listings():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT c.id, c.year, c.make, c.model, c.mileage, c.status, c.created_at,
                   s.email as seller_email,
                   (SELECT COUNT(*) FROM offers o WHERE o.car_id = c.id) as bid_count,
                   (SELECT MAX(offer_amount) FROM offers o WHERE o.car_id = c.id) as top_bid
            FROM cars c
            LEFT JOIN sellers s ON c.seller_id = s.id
            ORDER BY c.created_at DESC
            LIMIT 50
        """)
        rows = cur.fetchall()
        return [{"car_id": str(r[0]), "year": r[1], "make": r[2], "model": r[3],
                 "mileage": r[4], "status": r[5], "created_at": str(r[6]),
                 "seller_email": r[7], "bid_count": r[8], "top_bid": float(r[9]) if r[9] else 0} for r in rows]
    finally:
        cur.close()
        conn.close()



@router.get("/{car_id}")
def get_car(car_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, seller_id, year, make, model, mileage, zip,
                   condition, created_at, status, vin, title_status,
                   loan_status, trim, color, transmission, drivetrain,
                   keys, accidents, owners, smoked_in, overall_condition,
                   comments, addons, photos
            FROM cars WHERE id = %s
        """, (car_id,))
        c = cur.fetchone()
        if not c:
            raise HTTPException(status_code=404, detail="Car not found")
        photos = c[24]
        if isinstance(photos, str):
            import json
            try: photos = json.loads(photos)
            except: photos = []
        return {
            "car_id": str(c[0]), "seller_id": str(c[1]),
            "year": c[2], "make": c[3], "model": c[4],
            "mileage": c[5], "zip": c[6], "condition": c[7],
            "created_at": str(c[8]), "status": c[9],
            "vin": c[10] or '', "title_status": c[11] or 'Clean',
            "loan_status": c[12] or 'None', "trim": c[13] or '',
            "color": c[14] or '', "transmission": c[15] or '',
            "drivetrain": c[16] or '', "keys": c[17] or '',
            "accidents": c[18] or 'None', "owners": c[19] or 1,
            "smoked_in": c[20] or False, "overall_condition": c[21] or '',
            "comments": c[22] or '', "addons": c[23] or '',
            "photos": photos or []
        }
    finally:
        cur.close()
        conn.close()
