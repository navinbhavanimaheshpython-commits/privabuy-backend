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
