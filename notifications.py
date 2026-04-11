# notifications.py
from email.message import EmailMessage
import smtplib
from database import get_connection  # adjust based on your project

def notify_dealers_about_car(car_id: str, car):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT dealer_name, email FROM dealers")
    dealers = cur.fetchall()

    conn.close()

    subject = f"New Car Listing: {car.year} {car.make} {car.model}"
    body = f"""
A new car has been listed.

Car ID: {car_id}
Year: {car.year}
Make: {car.make}
Model: {car.model}
Mileage: {car.mileage}
Zip: {car.zip}

Submit your offer here:
http://localhost:8000/offer/{car_id}
"""

    for dealer_name, email in dealers:
        send_email(email, subject, body)


def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = "YOUR_EMAIL@gmail.com"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("YOUR_EMAIL@gmail.com", "YOUR_APP_PASSWORD")
        smtp.send_message(msg)
