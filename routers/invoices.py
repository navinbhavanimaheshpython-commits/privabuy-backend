from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import resend
import os
import psycopg2
import uuid
 
router = APIRouter()
 
resend.api_key = os.environ.get("RESEND_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")
 
def get_db():
    return psycopg2.connect(DATABASE_URL)
 
class InvoiceRequest(BaseModel):
    dealer_id: str
    dealer_fee: int = 200
    win_price: float
 
def generate_invoice_number(conn) -> str:
    year = datetime.now().year
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM invoices WHERE created_at >= date_trunc('year', NOW())")
    count = cur.fetchone()[0] + 1
    cur.close()
    return f"PB-{year}-{str(count).zfill(4)}"
 
def build_invoice_email(invoice_number: str, dealer_name: str, vehicle: str,
                         win_price: float, dealer_fee: int, due_date: str) -> str:
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: 'Inter', Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 0; }}
    .wrapper {{ max-width: 600px; margin: 40px auto; background: #ffffff; border: 1px solid rgba(0,0,0,0.12); border-radius: 16px; overflow: hidden; }}
    .header {{ background: #1a1814; padding: 32px 40px; }}
    .logo {{ font-size: 26px; color: #ffffff; font-style: italic; letter-spacing: -0.02em; }}
    .logo span {{ color: #9474d4; }}
    .header-sub {{ font-size: 12px; color: rgba(255,255,255,0.45); margin-top: 4px; letter-spacing: 0.08em; text-transform: uppercase; }}
    .body {{ padding: 40px; }}
    .invoice-title {{ font-size: 22px; font-weight: 700; color: #1a1814; margin-bottom: 4px; }}
    .invoice-sub {{ font-size: 13px; color: rgba(0,0,0,0.5); margin-bottom: 32px; }}
    .info-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
    .info-label {{ font-size: 12px; color: rgba(0,0,0,0.45); text-transform: uppercase; letter-spacing: 0.07em; }}
    .info-value {{ font-size: 13px; font-weight: 600; color: #1a1814; }}
    .divider {{ height: 1px; background: rgba(0,0,0,0.08); margin: 24px 0; }}
    .line-items {{ background: #f8f8f8; border: 1px solid rgba(0,0,0,0.10); border-radius: 10px; overflow: hidden; margin-bottom: 24px; }}
    .line-item {{ display: flex; justify-content: space-between; align-items: center; padding: 14px 20px; border-bottom: 1px solid rgba(0,0,0,0.07); }}
    .line-item:last-child {{ border-bottom: none; }}
    .line-desc {{ font-size: 13px; color: #1a1814; }}
    .line-desc small {{ display: block; font-size: 11px; color: rgba(0,0,0,0.45); margin-top: 2px; }}
    .line-amount {{ font-size: 15px; font-weight: 700; color: #1a1814; }}
    .total-row {{ display: flex; justify-content: space-between; align-items: center; padding: 16px 20px; background: #1a1814; border-radius: 10px; margin-bottom: 24px; }}
    .total-label {{ font-size: 13px; color: rgba(255,255,255,0.7); }}
    .total-amount {{ font-size: 22px; font-weight: 700; color: #9474d4; }}
    .pay-box {{ background: rgba(148,116,212,0.08); border: 1.5px solid rgba(148,116,212,0.25); border-radius: 12px; padding: 20px; margin-bottom: 24px; }}
    .pay-title {{ font-size: 13px; font-weight: 700; color: #1a1814; margin-bottom: 10px; }}
    .pay-line {{ font-size: 13px; color: rgba(0,0,0,0.65); margin-bottom: 6px; line-height: 1.6; }}
    .pay-line strong {{ color: #1a1814; }}
    .footer {{ background: #f8f8f8; padding: 24px 40px; border-top: 1px solid rgba(0,0,0,0.08); }}
    .footer-text {{ font-size: 12px; color: rgba(0,0,0,0.45); line-height: 1.7; }}
    .footer-text a {{ color: #7c5cbf; text-decoration: none; }}
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="header">
      <div class="logo">Priva<span>Buy</span></div>
      <div class="header-sub">Dealer Invoice</div>
    </div>
 
    <div class="body">
      <div class="invoice-title">Invoice {invoice_number}</div>
      <div class="invoice-sub">Issued {datetime.now().strftime('%B %d, %Y')} · Due by check on next collection date</div>
 
      <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
        <tr>
          <td style="padding-bottom:8px;">
            <div style="font-size:12px;color:rgba(0,0,0,0.45);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;">Bill To</div>
            <div style="font-size:14px;font-weight:600;color:#1a1814;">{dealer_name}</div>
          </td>
          <td align="right" style="padding-bottom:8px;">
            <div style="font-size:12px;color:rgba(0,0,0,0.45);text-transform:uppercase;letter-spacing:0.07em;margin-bottom:4px;">Vehicle</div>
            <div style="font-size:13px;font-weight:600;color:#1a1814;">{vehicle}</div>
            <div style="font-size:12px;color:rgba(0,0,0,0.45);">Win price: ${win_price:,.0f}</div>
          </td>
        </tr>
      </table>
 
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f8f8;border:1px solid rgba(0,0,0,0.10);border-radius:10px;overflow:hidden;margin-bottom:16px;">
        <tr style="border-bottom:1px solid rgba(0,0,0,0.07);">
          <td style="padding:14px 20px;">
            <div style="font-size:13px;color:#1a1814;font-weight:500;">PrivaBuy Dealer Platform Fee</div>
            <div style="font-size:11px;color:rgba(0,0,0,0.45);margin-top:2px;">Facilitation fee for auction win · {vehicle}</div>
          </td>
          <td align="right" style="padding:14px 20px;">
            <div style="font-size:15px;font-weight:700;color:#1a1814;">${dealer_fee}</div>
          </td>
        </tr>
      </table>
 
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#1a1814;border-radius:10px;margin-bottom:24px;">
        <tr>
          <td style="padding:16px 20px;">
            <span style="font-size:13px;color:rgba(255,255,255,0.7);">Total Due</span>
          </td>
          <td align="right" style="padding:16px 20px;">
            <span style="font-size:22px;font-weight:700;color:#9474d4;">${dealer_fee}.00</span>
          </td>
        </tr>
      </table>
 
      <div style="background:rgba(148,116,212,0.08);border:1.5px solid rgba(148,116,212,0.25);border-radius:12px;padding:20px;margin-bottom:24px;">
        <div style="font-size:13px;font-weight:700;color:#1a1814;margin-bottom:10px;">✏️ How to Pay</div>
        <div style="font-size:13px;color:rgba(0,0,0,0.65);line-height:1.7;">
          Write a check for <strong style="color:#1a1814;">${dealer_fee}.00</strong> payable to:<br>
          <strong style="color:#1a1814;font-size:15px;">PrivaBuy LLC</strong><br><br>
          Navin will collect checks on the <strong style="color:#1a1814;">5th, 15th, and 20th</strong> of each month.<br>
          Have your check ready at your dealership on the next collection date.
        </div>
      </div>
 
      <div style="font-size:12px;color:rgba(0,0,0,0.45);line-height:1.7;">
        Questions? Reply to this email or contact <a href="mailto:navin@privabuy.com" style="color:#7c5cbf;">navin@privabuy.com</a>
      </div>
    </div>
 
    <div style="background:#f8f8f8;padding:24px 40px;border-top:1px solid rgba(0,0,0,0.08);">
      <div style="font-size:12px;color:rgba(0,0,0,0.45);line-height:1.7;">
        PrivaBuy LLC · 5634-7 Old Dover Blvd, Fort Wayne, IN 46835<br>
        Invoice {invoice_number} · {datetime.now().strftime('%B %d, %Y')}
      </div>
    </div>
  </div>
</body>
</html>
"""
 
 
@router.post("/transactions/{txn_id}/send-dealer-invoice")
async def send_dealer_invoice(txn_id: str, payload: InvoiceRequest):
    conn = get_db()
    try:
        cur = conn.cursor()
 
        # Get transaction + dealer + vehicle details
        cur.execute("""
            SELECT t.amount, t.car_id,
                   d.dealer_name, d.email,
                   c.year, c.make, c.model
            FROM transactions t
            JOIN dealers d ON d.id = t.dealer_id::uuid
            JOIN cars c ON c.car_id = t.car_id
            WHERE t.transaction_id = %s
        """, (txn_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Transaction not found")
 
        win_price, car_id, dealer_name, dealer_email, year, make, model = row
        vehicle = f"{year} {make} {model}"
 
        # Check if invoice already sent for this transaction
        cur.execute("SELECT invoice_number FROM invoices WHERE transaction_id = %s", (txn_id,))
        existing = cur.fetchone()
        if existing:
            return {"invoice_number": existing[0], "already_sent": True}
 
        # Generate invoice number
        invoice_number = generate_invoice_number(conn)
 
        # Save to DB
        cur.execute("""
            INSERT INTO invoices (invoice_number, transaction_id, dealer_id, dealer_email,
                                  dealer_name, vehicle, win_price, amount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (invoice_number, txn_id, payload.dealer_id, dealer_email,
              dealer_name, vehicle, float(win_price), payload.dealer_fee))
        conn.commit()
 
        # Send email via Resend
        due_date = (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")
        html = build_invoice_email(invoice_number, dealer_name, vehicle,
                                   float(win_price), payload.dealer_fee, due_date)
 
        resend.Emails.send({
            "from": "PrivaBuy <navin@privabuy.com>",
            "to": [dealer_email],
            "bcc": ["navin@privabuy.com"],   # you get a copy of every invoice
            "subject": f"Invoice {invoice_number} — PrivaBuy Dealer Fee · {vehicle}",
            "html": html,
        })
 
        cur.close()
        return {
            "invoice_number": invoice_number,
            "dealer_name":    dealer_name,
            "dealer_email":   dealer_email,
            "vehicle":        vehicle,
            "amount":         payload.dealer_fee,
            "sent":           True
        }
 
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
 