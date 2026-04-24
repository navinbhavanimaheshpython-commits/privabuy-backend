from fastapi import APIRouter
from pydantic import BaseModel
import uuid
from datetime import datetime
from database import get_connection


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
            comments, addons)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'open',
            %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (car_id, data.seller_id, data.year, data.make, data.model,
              data.mileage, data.zip, data.condition, data.seller_phone,
              data.seller_email, datetime.utcnow(),
              data.vin, data.title_status, data.loan_status, data.trim,
              data.color, data.transmission, data.drivetrain, data.keys,
              data.accidents, data.owners, data.smoked_in,
              data.overall_condition, data.comments, data.addons))

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


@router.get("/{car_id}")
def get_car(car_id: str):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id, seller_id, year, make, model, mileage, zip, 
                   condition, created_at, status
            FROM cars WHERE id = %s
        """, (car_id,))
        c = cur.fetchone()
        if not c:
            raise HTTPException(status_code=404, detail="Car not found")
        return {
            "car_id": str(c[0]), "seller_id": str(c[1]),
            "year": c[2], "make": c[3], "model": c[4],
            "mileage": c[5], "zip": c[6], "condition": c[7],
            "created_at": str(c[8]), "status": c[9]
        }
    finally:
        cur.close()
        conn.close()