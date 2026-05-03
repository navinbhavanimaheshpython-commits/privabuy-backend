import resend

resend.api_key = "re_Z8YiTFC9_Fj3vB5a5nhZujaUtWrY4thQm"

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