import resend

import os
resend.api_key = os.environ.get("RESEND_API_KEY")

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
                <a href="https://privabuy.com/app?role=dealer" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View Auction →</a>
                <p style="color:#999;font-size:12px;margin-top:24px;">You're receiving this because you're a registered dealer on PrivaBuy.</p>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"Email error: {e}")

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
                <a href="https://privabuy.com/app?role=seller" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin:16px 0;">View My Auction →</a>
                <p style="color:#999;font-size:12px;margin-top:24px;">You're receiving this because you listed a vehicle on PrivaBuy.</p>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"Email error: {e}")



def send_admin_new_dealer(dealer_name: str, contact_name: str, email: str, license: str, city: str, state: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": "navinbhavanimaheshpython@gmail.com",
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
                <a href="https://privabuy.com/app?role=admin" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:20px;">Review in Admin Panel →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"Admin email error: {e}")

def send_dealer_welcome(dealer_email: str, contact_name: str, dealer_name: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": dealer_email,
            "subject": f"Welcome to PrivaBuy, {dealer_name} 🚗",
            "html": f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f5f5f5;padding:20px;">
              <div style="background:#080808;padding:32px 24px;border-radius:12px;margin-bottom:20px;text-align:center;">
                <h1 style="color:#c9b8ff;font-size:26px;margin:0 0 6px;">PrivaBuy</h1>
                <p style="color:rgba(255,255,255,0.45);margin:0;font-size:13px;">Dealer Network</p>
              </div>
              <div style="background:white;padding:28px 24px;border-radius:12px;margin-bottom:12px;">
                <h2 style="color:#1a1a1a;margin:0 0 10px;font-size:20px;">Welcome, {contact_name} 👋</h2>
                <p style="color:#555;line-height:1.7;margin:0 0 20px;font-size:14px;">
                  You're now part of the PrivaBuy dealer network. Here's a quick rundown of how the platform works and what to expect.
                </p>

                <div style="border-top:1px solid #f0f0f0;padding-top:20px;margin-bottom:20px;">
                  <p style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#999;margin:0 0 16px;">What is PrivaBuy?</p>
                  <p style="color:#555;line-height:1.7;font-size:14px;margin:0;">
                    PrivaBuy is a two-sided vehicle marketplace that connects <strong>private sellers</strong> of 6–8 year old, higher-mileage vehicles directly with <strong>franchised dealers</strong> through real-time competitive auctions. No cold calls. No scraping listings. Motivated sellers come to you.
                  </p>
                </div>

                <div style="border-top:1px solid #f0f0f0;padding-top:20px;margin-bottom:8px;">
                  <p style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#999;margin:0 0 16px;">How It Works</p>

                  <div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:14px;">
                    <div style="background:#f5f0ff;color:#7c5cbf;font-size:13px;font-weight:700;border-radius:50%;width:28px;height:28px;min-width:28px;display:flex;align-items:center;justify-content:center;">1</div>
                    <div>
                      <p style="margin:0 0 3px;font-size:14px;font-weight:600;color:#1a1a1a;">Seller Lists a Vehicle</p>
                      <p style="margin:0;font-size:13px;color:#777;line-height:1.5;">A private seller submits their vehicle with photos, condition details, and a vehicle history report. You get notified immediately if it's in your territory.</p>
                    </div>
                  </div>

                  <div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:14px;">
                    <div style="background:#f5f0ff;color:#7c5cbf;font-size:13px;font-weight:700;border-radius:50%;width:28px;height:28px;min-width:28px;display:flex;align-items:center;justify-content:center;">2</div>
                    <div>
                      <p style="margin:0 0 3px;font-size:14px;font-weight:600;color:#1a1a1a;">You Bid — Up to 5 Dealers Max</p>
                      <p style="margin:0;font-size:13px;color:#777;line-height:1.5;">Auctions are open-ended with no forced close. You bid when you're ready. No subscription, no seat fee — pay only when you win.</p>
                    </div>
                  </div>

                  <div style="display:flex;gap:14px;align-items:flex-start;margin-bottom:14px;">
                    <div style="background:#f5f0ff;color:#7c5cbf;font-size:13px;font-weight:700;border-radius:50%;width:28px;height:28px;min-width:28px;display:flex;align-items:center;justify-content:center;">3</div>
                    <div>
                      <p style="margin:0 0 3px;font-size:14px;font-weight:600;color:#1a1a1a;">Seller Accepts — Deal Flow Begins</p>
                      <p style="margin:0;font-size:13px;color:#777;line-height:1.5;">When a seller accepts your bid, PrivaBuy guides both of you through payment confirmation, bill of sale, pickup scheduling, and vehicle inspection — step by step.</p>
                    </div>
                  </div>

                  <div style="display:flex;gap:14px;align-items:flex-start;">
                    <div style="background:#f5f0ff;color:#7c5cbf;font-size:13px;font-weight:700;border-radius:50%;width:28px;height:28px;min-width:28px;display:flex;align-items:center;justify-content:center;">4</div>
                    <div>
                      <p style="margin:0 0 3px;font-size:14px;font-weight:600;color:#1a1a1a;">Vehicle is Yours</p>
                      <p style="margin:0;font-size:13px;color:#777;line-height:1.5;">You pay the seller directly at pickup. PrivaBuy collects a flat dealer fee only after the deal closes. <strong>Your first 5 wins are free</strong> as an early partner.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div style="background:white;padding:20px 24px;border-radius:12px;margin-bottom:12px;">
                <p style="font-size:11px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#999;margin:0 0 12px;">Your Early Partner Benefits</p>
                <table style="width:100%;border-collapse:collapse;">
                  <tr><td style="padding:7px 0;border-bottom:1px solid #f5f5f5;color:#555;font-size:13px;">✅ First 5 vehicle wins</td><td style="padding:7px 0;border-bottom:1px solid #f5f5f5;text-align:right;font-weight:600;color:#1a1a1a;font-size:13px;">Free</td></tr>
                  <tr><td style="padding:7px 0;border-bottom:1px solid #f5f5f5;color:#555;font-size:13px;">📋 VinAudit history report on every listing</td><td style="padding:7px 0;border-bottom:1px solid #f5f5f5;text-align:right;font-weight:600;color:#1a1a1a;font-size:13px;">Included</td></tr>
                  <tr><td style="padding:7px 0;border-bottom:1px solid #f5f5f5;color:#555;font-size:13px;">📍 Local inventory only</td><td style="padding:7px 0;border-bottom:1px solid #f5f5f5;text-align:right;font-weight:600;color:#1a1a1a;font-size:13px;">Your territory</td></tr>
                  <tr><td style="padding:7px 0;color:#555;font-size:13px;">💳 Pay per win — no subscription</td><td style="padding:7px 0;text-align:right;font-weight:600;color:#1a1a1a;font-size:13px;">$500/vehicle</td></tr>
                </table>
              </div>

              <div style="text-align:center;padding:20px 0 8px;">
                <a href="{PORTAL_URL}?role=dealer" style="display:inline-block;background:#7c5cbf;color:#fff;padding:13px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;">Go to Your Dealer Portal →</a>
                <p style="margin:14px 0 0;font-size:12px;color:#aaa;">Questions? Reply to this email or reach us at <a href="mailto:navin@privabuy.com" style="color:#7c5cbf;">navin@privabuy.com</a></p>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"[send_dealer_welcome] {e}")

def send_admin_new_seller(name: str, email: str, phone: str):
    try:
        resend.Emails.send({
            "from": "PrivaBuy <notifications@privabuy.com>",
            "to": "navinbhavanimaheshpython@gmail.com",
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
                <a href="https://privabuy.com/app?role=admin" style="display:inline-block;background:#c9b8ff;color:#080808;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;margin-top:20px;">View in Admin Panel →</a>
              </div>
            </div>
            """
        })
    except Exception as e:
        print(f"Admin email error: {e}")    



def send_password_reset(email: str, name: str, token: str):
    try:
        reset_url = f"https://privabuy.com/reset-password?token={token}"
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
        print(f"Reset email error: {e}")
# ─── DEAL FLOW NOTIFICATIONS ─────────────────────────────────────────────────

def send_dealer_bid_accepted(dealer_email: str, dealer_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": dealer_email,"subject": f"You Won! {year} {make} {model} — Pay $600 to Proceed","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Your bid was accepted!</h2><p>Congratulations {dealer_name} — the seller accepted your bid of <strong>${amount:,.0f}</strong> for the {year} {make} {model}.</p><p>Pay your $600 platform fee within 24 hours or your bid will be forfeited.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Pay $600 Now</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_bid_accepted_confirmation(seller_email: str, seller_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Offer Accepted — {year} {make} {model} for ${amount:,.0f}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>You accepted an offer!</h2><p>Hi {seller_name}, you accepted <strong>${amount:,.0f}</strong> for your {year} {make} {model}. The dealer has 24 hours to pay their $600 fee.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_dealer_paid_fee(seller_email: str, seller_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Paid — Sign Bill of Sale for {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Dealer paid their fee!</h2><p>Hi {seller_name}, the dealer paid their $600 fee for your {year} {make} {model}. Please sign the Bill of Sale to continue.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Sign Bill of Sale</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_dealer_seller_signed_bos(dealer_email: str, dealer_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": dealer_email,"subject": f"Seller Signed Bill of Sale — {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Seller signed the Bill of Sale</h2><p>Hi {dealer_name}, the seller signed the Bill of Sale for the {year} {make} {model}. Please sign yours to proceed.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Sign Now</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_dealer_signed_bos(seller_email: str, seller_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Signed Bill of Sale — {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Dealer signed — both parties done!</h2><p>Hi {seller_name}, the dealer signed the Bill of Sale. Pickup scheduling will begin shortly.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_pickup_slots_proposed(seller_email: str, seller_name: str, year: int, make: str, model: str, slot_1: str, slot_2: str, slot_3: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Proposed Pickup Times — {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Pickup times proposed</h2><p>Hi {seller_name}, the dealer proposed these times for the {year} {make} {model}:<br><br><strong>Option 1:</strong> {slot_1}<br><strong>Option 2:</strong> {slot_2}<br><strong>Option 3:</strong> {slot_3}</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Choose a Time</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_dealer_pickup_confirmed(dealer_email: str, dealer_name: str, year: int, make: str, model: str, pickup_time: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": dealer_email,"subject": f"Pickup Confirmed — {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Pickup confirmed!</h2><p>Hi {dealer_name}, the seller confirmed pickup for the {year} {make} {model}.</p><p><strong>Time:</strong> {pickup_time}</p><p>After pickup, confirm the vehicle condition in your Deal Flow tab.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_pickup_confirmed(seller_email: str, seller_name: str, year: int, make: str, model: str, pickup_time: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Pickup Confirmed — {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Pickup locked in!</h2><p>Hi {seller_name}, pickup for your {year} {make} {model} is confirmed for <strong>{pickup_time}</strong>. Have your title ready.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_vehicle_confirmed(seller_email: str, seller_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Confirmed Vehicle — Confirm Payment for {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Dealer confirmed the vehicle!</h2><p>Hi {seller_name}, the dealer confirmed the {year} {make} {model} is as described. Please confirm when you receive their payment of <strong>${amount:,.0f}</strong>.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Confirm Payment Received</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_payment_confirmed_complete(seller_email: str, seller_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Last Step — Pay Your $250 PrivaBuy Fee for {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Almost done!</h2><p>Hi {seller_name}, payment confirmed. Pay your $250 PrivaBuy platform fee to complete the deal.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Pay $250 Fee</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_deal_complete(seller_email: str, seller_name: str, dealer_email: str, dealer_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    for email, name in [(seller_email, seller_name), (dealer_email, dealer_name)]:
        try:
            resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": email,"subject": f"Deal Complete — {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Deal complete!</h2><p>Hi {name}, the sale of the {year} {make} {model} for <strong>${amount:,.0f}</strong> is fully complete. Thank you for using PrivaBuy!</p></div>"})
        except Exception as e:
            print(f"Email error: {e}")

# ─── DEAL FLOW NOTIFICATIONS ─────────────────────────────────────────────────

def send_dealer_bid_accepted(dealer_email: str, dealer_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": dealer_email,"subject": f"You Won! {year} {make} {model} - Pay $600 to Proceed","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Your bid was accepted!</h2><p>Congratulations {dealer_name} - the seller accepted your bid of <strong>${amount:,.0f}</strong> for the {year} {make} {model}.</p><p>Pay your $600 platform fee within 24 hours or your bid will be forfeited.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Pay $600 Now</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_bid_accepted_confirmation(seller_email: str, seller_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Offer Accepted - {year} {make} {model} for ${amount:,.0f}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>You accepted an offer!</h2><p>Hi {seller_name}, you accepted <strong>${amount:,.0f}</strong> for your {year} {make} {model}. The dealer has 24 hours to pay their $600 fee.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_dealer_paid_fee(seller_email: str, seller_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Paid - Sign Bill of Sale for {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Dealer paid their fee!</h2><p>Hi {seller_name}, the dealer paid their $600 fee for your {year} {make} {model}. Please sign the Bill of Sale to continue.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Sign Bill of Sale</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_dealer_seller_signed_bos(dealer_email: str, dealer_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": dealer_email,"subject": f"Seller Signed Bill of Sale - {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Seller signed the Bill of Sale</h2><p>Hi {dealer_name}, the seller signed for the {year} {make} {model}. Please sign yours to proceed.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Sign Now</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_dealer_signed_bos(seller_email: str, seller_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Signed Bill of Sale - {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Both parties signed!</h2><p>Hi {seller_name}, the dealer signed the Bill of Sale for your {year} {make} {model}. Pickup scheduling will begin shortly.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_pickup_slots_proposed(seller_email: str, seller_name: str, year: int, make: str, model: str, slot_1: str, slot_2: str, slot_3: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Proposed Pickup Times - {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Pickup times proposed</h2><p>Hi {seller_name}, the dealer proposed these times for the {year} {make} {model}:<br><br><strong>Option 1:</strong> {slot_1}<br><strong>Option 2:</strong> {slot_2}<br><strong>Option 3:</strong> {slot_3}</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Choose a Time</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_dealer_pickup_confirmed(dealer_email: str, dealer_name: str, year: int, make: str, model: str, pickup_time: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": dealer_email,"subject": f"Pickup Confirmed - {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Pickup confirmed!</h2><p>Hi {dealer_name}, seller confirmed pickup for the {year} {make} {model} at <strong>{pickup_time}</strong>. After pickup confirm vehicle condition in your Deal Flow tab.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_pickup_confirmed(seller_email: str, seller_name: str, year: int, make: str, model: str, pickup_time: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Pickup Confirmed - {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Pickup locked in!</h2><p>Hi {seller_name}, pickup for your {year} {make} {model} is confirmed for <strong>{pickup_time}</strong>. Have your title ready.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_vehicle_confirmed(seller_email: str, seller_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Dealer Confirmed Vehicle - Confirm Payment for {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Dealer confirmed the vehicle!</h2><p>Hi {seller_name}, the dealer confirmed the {year} {make} {model} is as described. Please confirm when you receive their payment of <strong>${amount:,.0f}</strong>.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Confirm Payment Received</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_payment_confirmed_complete(seller_email: str, seller_name: str, year: int, make: str, model: str):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    try:
        resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": seller_email,"subject": f"Last Step - Pay Your $250 PrivaBuy Fee for {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Almost done!</h2><p>Hi {seller_name}, payment confirmed for your {year} {make} {model}. Pay your $250 PrivaBuy platform fee to complete the deal.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;'>Pay $250 Fee</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_deal_complete(seller_email: str, seller_name: str, dealer_email: str, dealer_name: str, year: int, make: str, model: str, amount: float):
    import resend, os
    resend.api_key = os.environ.get("RESEND_API_KEY", "")
    for email, name in [(seller_email, seller_name), (dealer_email, dealer_name)]:
        try:
            resend.Emails.send({"from": "PrivaBuy <noreply@privabuy.com>","to": email,"subject": f"Deal Complete - {year} {make} {model}","html": f"<div style='font-family:Inter,sans-serif;padding:32px;'><h2>Deal complete!</h2><p>Hi {name}, the sale of the {year} {make} {model} for <strong>${amount:,.0f}</strong> is fully complete. Thank you for using PrivaBuy!</p></div>"})
        except Exception as e:
            print(f"Email error: {e}")
