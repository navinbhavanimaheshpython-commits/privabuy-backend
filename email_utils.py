import resend
import os

resend.api_key = os.environ.get("RESEND_API_KEY")

PORTAL_URL = "https://privabuy.com/portal.html"
ADMIN_EMAIL = "navinbhavanimaheshpython@gmail.com"


# ─── EXISTING FUNCTIONS (unchanged) ─────────────────────────────────────────

def send_dealer_new_listing(dealer_email: str, dealer_name: str, year: int, make: str, model: str, mileage: int, zip: str, car_id: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": dealer_email,
            "subject": f"New Listing: {year} {make} {model} in your territory",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Dealer Notifications</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">New Vehicle Listed in Your Territory</h2>
                <div style="background:#f8f8f8;padding:16px;border-radius:8px;margin-bottom:20px;">
                  <h3 style="margin:0 0 8px;color:#1a1a1a;">{year} {make} {model}</h3>
                  <p style="margin:4px 0;color:#666;">{mileage:,} miles · ZIP {zip}</p>
                </div>
                <p style="color:#444;">Hi {dealer_name},</p>
                <p style="color:#444;">A new vehicle matching your territory has just been listed on PrivaBuy. Log in now to place your bid before other dealers.</p>
                <a href="{PORTAL_URL}?role=dealer" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View Auction →</a>
                <p style="color:#999;font-size:12px;margin-top:24px;">You're receiving this because you're a registered dealer on PrivaBuy.</p>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_dealer_new_listing] {e}")


def send_seller_new_bid(seller_email: str, dealer_label: str, amount: int, year: int, make: str, model: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": seller_email,
            "subject": f"New Bid on Your {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Seller Notifications</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">You Have a New Bid!</h2>
                <div style="background:#f0f0ff;padding:16px;border-radius:8px;margin-bottom:20px;text-align:center;">
                  <p style="margin:0;color:#666;font-size:14px;">Current Top Bid</p>
                  <h2 style="margin:8px 0;color:#7c5cbf;font-size:36px;">${amount:,}</h2>
                  <p style="margin:0;color:#666;">{year} {make} {model}</p>
                </div>
                <p style="color:#444;">A dealer just placed a bid on your vehicle. Log in to see all bids and accept when you're ready.</p>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View My Auction →</a>
                <p style="color:#999;font-size:12px;margin-top:24px;">You're receiving this because you listed a vehicle on PrivaBuy.</p>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_new_bid] {e}")


def send_admin_new_dealer(dealer_name: str, contact_name: str, email: str, license: str, city: str, state: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": ADMIN_EMAIL,
            "subject": f"New Dealer Registration: {dealer_name}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy Admin</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">New Dealer Registration</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">New Dealer Registered</h2>
                <table style="width:100%;border-collapse:collapse;">
                  <tr><td style="padding:8px 0;color:#666;width:140px;">Dealership</td><td style="padding:8px 0;font-weight:600;">{dealer_name}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Contact</td><td style="padding:8px 0;">{contact_name}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Email</td><td style="padding:8px 0;">{email}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">License</td><td style="padding:8px 0;font-family:monospace;">{license}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Location</td><td style="padding:8px 0;">{city}, {state}</td></tr>
                </table>
                <a href="{PORTAL_URL}?role=admin" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:20px;">Review in Admin Panel →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_admin_new_dealer] {e}")


def send_admin_new_seller(name: str, email: str, phone: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": ADMIN_EMAIL,
            "subject": f"New Seller Registration: {email}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy Admin</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">New Seller Registration</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">New Seller Registered</h2>
                <table style="width:100%;border-collapse:collapse;">
                  <tr><td style="padding:8px 0;color:#666;width:140px;">Name</td><td style="padding:8px 0;font-weight:600;">{name}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Email</td><td style="padding:8px 0;">{email}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Phone</td><td style="padding:8px 0;">{phone}</td></tr>
                </table>
                <a href="{PORTAL_URL}?role=admin" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:20px;">View in Admin Panel →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_admin_new_seller] {e}")

        


def send_password_reset(email: str, name: str, token: str):
    reset_url = f"https://privabuy.com/reset-password?token={token}"
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": email,
            "subject": "Reset Your PrivaBuy Password",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Password Reset</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Reset Your Password</h2>
                <p style="color:#444;">Hi {name},</p>
                <p style="color:#444;">We received a request to reset your PrivaBuy password. Click the button below to choose a new one. This link expires in 1 hour.</p>
                <a href="{reset_url}" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">Reset Password →</a>
                <p style="color:#999;font-size:12px;margin-top:24px;">If you didn't request this, ignore this email. Your password won't change.</p>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_password_reset] {e}")


# ─── DEAL FLOW NOTIFICATIONS ─────────────────────────────────────────────────

def send_dealer_bid_accepted(dealer_email: str, dealer_name: str, year: int, make: str, model: str, amount: float):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": dealer_email,
            "subject": f"You Won — {year} {make} {model} · Confirm Your Win",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Your Bid Was Accepted!</h2>
                <p style="color:#444;">Congratulations {dealer_name} — the seller accepted your bid of <strong>${amount:,.0f}</strong> for the <strong>{year} {make} {model}</strong>.</p>
                <p style="color:#444;">Sign the facilitation acknowledgement and confirm your win in Deal Flow. Your $200 dealer fee invoice will be sent once you confirm.</p>
                <a href="{PORTAL_URL}?role=dealer" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">Confirm Win in Deal Flow →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_dealer_bid_accepted] {e}")


def send_seller_bid_accepted_confirmation(seller_email: str, seller_name: str, year: int, make: str, model: str, amount: float):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": seller_email,
            "subject": f"Offer Accepted — {year} {make} {model} for ${amount:,.0f}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">You Accepted an Offer</h2>
                <p style="color:#444;">Hi {seller_name}, you accepted <strong>${amount:,.0f}</strong> for your <strong>{year} {make} {model}</strong>.</p>
                <p style="color:#444;">The dealer will be notified to confirm their win. Once they do, you'll both sign the Bill of Sale and move to pickup scheduling.</p>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View Deal Flow →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_bid_accepted_confirmation] {e}")


def send_seller_dealer_paid_fee(seller_email: str, seller_name: str, year: int, make: str, model: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": seller_email,
            "subject": f"Dealer Confirmed — Sign Bill of Sale for {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Dealer Confirmed — Your Turn</h2>
                <p style="color:#444;">Hi {seller_name}, the dealer confirmed their win for your <strong>{year} {make} {model}</strong>. Please sign the Bill of Sale to continue.</p>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">Sign Bill of Sale →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_dealer_paid_fee] {e}")


def send_dealer_seller_signed_bos(dealer_email: str, dealer_name: str, year: int, make: str, model: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": dealer_email,
            "subject": f"Seller Signed Bill of Sale — {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Seller Signed the Bill of Sale</h2>
                <p style="color:#444;">Hi {dealer_name}, the seller signed the Bill of Sale for the <strong>{year} {make} {model}</strong>. Please sign yours to move to pickup scheduling.</p>
                <a href="{PORTAL_URL}?role=dealer" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">Sign Now →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_dealer_seller_signed_bos] {e}")


def send_seller_dealer_signed_bos(seller_email: str, seller_name: str, year: int, make: str, model: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": seller_email,
            "subject": f"Both Parties Signed — Pickup Scheduling Begins for {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Both Parties Signed ✓</h2>
                <p style="color:#444;">Hi {seller_name}, the dealer signed the Bill of Sale for your <strong>{year} {make} {model}</strong>. The dealer will now propose pickup times — you'll receive another email as soon as they do.</p>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View Deal Flow →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_dealer_signed_bos] {e}")


def send_seller_pickup_slots_proposed(seller_email: str, seller_name: str, year: int, make: str, model: str, slot_1: str, slot_2: str, slot_3: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": seller_email,
            "subject": f"Dealer Proposed Pickup Times — Choose One for {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Choose a Pickup Time</h2>
                <p style="color:#444;">Hi {seller_name}, the dealer proposed these pickup times for your <strong>{year} {make} {model}</strong>:</p>
                <table style="width:100%;border-collapse:collapse;margin:16px 0;">
                  <tr><td style="padding:10px 0;color:#666;width:100px;border-bottom:1px solid #f0f0f0;">Option 1</td><td style="padding:10px 0;font-weight:600;border-bottom:1px solid #f0f0f0;">{slot_1}</td></tr>
                  <tr><td style="padding:10px 0;color:#666;border-bottom:1px solid #f0f0f0;">Option 2</td><td style="padding:10px 0;font-weight:600;border-bottom:1px solid #f0f0f0;">{slot_2}</td></tr>
                  <tr><td style="padding:10px 0;color:#666;">Option 3</td><td style="padding:10px 0;font-weight:600;">{slot_3}</td></tr>
                </table>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">Choose a Time →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_pickup_slots_proposed] {e}")


def send_dealer_pickup_confirmed(dealer_email: str, dealer_name: str, year: int, make: str, model: str, pickup_time: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": dealer_email,
            "subject": f"Pickup Confirmed — {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Pickup Time Confirmed ✓</h2>
                <p style="color:#444;">Hi {dealer_name}, the seller confirmed pickup for the <strong>{year} {make} {model}</strong>.</p>
                <p style="color:#444;"><strong>Time:</strong> {pickup_time}</p>
                <p style="color:#444;">Bring a check for the full bid amount. After pickup, confirm the vehicle condition in your Deal Flow tab.</p>
                <a href="{PORTAL_URL}?role=dealer" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View Deal Flow →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_dealer_pickup_confirmed] {e}")


def send_seller_pickup_confirmed(seller_email: str, seller_name: str, year: int, make: str, model: str, pickup_time: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": seller_email,
            "subject": f"Pickup Confirmed — {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Pickup Locked In ✓</h2>
                <p style="color:#444;">Hi {seller_name}, pickup for your <strong>{year} {make} {model}</strong> is confirmed for <strong>{pickup_time}</strong>.</p>
                <p style="color:#444;"><strong>Do not hand over the title until you receive payment in full.</strong></p>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View Deal Flow →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_pickup_confirmed] {e}")


def send_seller_vehicle_confirmed(seller_email: str, seller_name: str, year: int, make: str, model: str, amount: float):
    net = amount - 200
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": seller_email,
            "subject": f"Dealer Accepted the Vehicle — Confirm Payment for {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 16px;">Dealer Accepted the Vehicle</h2>
                <p style="color:#444;">Hi {seller_name}, the dealer confirmed your <strong>{year} {make} {model}</strong> is as described.</p>
                <p style="color:#444;">You should receive a check for <strong>${net:,.0f}</strong> (bid of ${amount:,.0f} minus the $200 PrivaBuy facilitation fee). Once you have it in hand, confirm receipt in Deal Flow and hand over the title.</p>
                <a href="{PORTAL_URL}?role=seller" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">Confirm Payment Received →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_seller_vehicle_confirmed] {e}")


def send_deal_complete(seller_email: str, seller_name: str, dealer_email: str, dealer_name: str, year: int, make: str, model: str, amount: float):
    for email, name, role in [
        (seller_email, seller_name, "seller"),
        (dealer_email, dealer_name, "dealer"),
    ]:
        try:
            resend.Emails.send({
                "from": "PrivaBuy <deals@privabuy.com>",
                "to": email,
                "subject": f"Deal Complete — {year} {make} {model}",
                "html": f"""
                <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
                  <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                    <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy</h1>
                    <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Deal Flow</p>
                  </div>
                  <div style="background:white;padding:24px;border-radius:12px;">
                    <h2 style="color:#1a1a1a;margin:0 0 16px;">Deal Complete 🎉</h2>
                    <p style="color:#444;">Hi {name}, the sale of the <strong>{year} {make} {model}</strong> for <strong>${amount:,.0f}</strong> is fully complete. Thank you for using PrivaBuy!</p>
                    <a href="{PORTAL_URL}?role={role}" style="display:inline-block;background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View History →</a>
                  </div>
                </div>
                """
            })
        except Exception as e:
            print(f"[send_deal_complete → {email}] {e}")


def send_admin_dispute_filed(txn_id: str, year: int, make: str, model: str, dealer_email: str, seller_email: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <deals@privabuy.com>",
            "to": ADMIN_EMAIL,
            "subject": f"⚠️ Dispute Filed — {year} {make} {model}",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:24px;border-radius:12px;margin-bottom:20px;">
                <h1 style="color:#c9b8ff;font-size:24px;margin:0;">PrivaBuy Admin</h1>
                <p style="color:rgba(255,255,255,0.5);margin:4px 0 0;">Dispute Alert</p>
              </div>
              <div style="background:white;padding:24px;border-radius:12px;">
                <h2 style="color:#d93025;margin:0 0 16px;">New Dispute Requires Review</h2>
                <table style="width:100%;border-collapse:collapse;">
                  <tr><td style="padding:8px 0;color:#666;width:140px;">Transaction ID</td><td style="padding:8px 0;font-family:monospace;font-size:12px;">{txn_id}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Vehicle</td><td style="padding:8px 0;font-weight:600;">{year} {make} {model}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Dealer</td><td style="padding:8px 0;">{dealer_email}</td></tr>
                  <tr><td style="padding:8px 0;color:#666;">Seller</td><td style="padding:8px 0;">{seller_email}</td></tr>
                </table>
                <a href="{PORTAL_URL}?role=admin" style="display:inline-block;background:#d93025;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:20px;">Review Dispute in Admin →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_admin_dispute_filed] {e}")