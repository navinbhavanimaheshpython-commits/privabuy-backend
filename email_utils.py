import resend

resend.api_key = "re_Z8YiTFC9_Fj3vB5a5nhZujaUtWrY4thQm"

def send_dealer_new_listing(dealer_email, dealer_name, year, make, model, mileage, zip, car_id):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":dealer_email,"subject":f"New Listing: {year} {make} {model} in your territory","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>New Vehicle Listed</h2><p>Hi {dealer_name}, a new {year} {make} {model} with {mileage:,} miles has been listed in ZIP {zip}.</p><a href='https://privabuy.com/app?role=dealer'>View Auction</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_new_bid(seller_email, dealer_label, amount, year, make, model):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"New Bid on Your {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>New Bid: ${amount:,}</h2><p>A dealer placed a bid on your {year} {make} {model}.</p><a href='https://privabuy.com/app?role=seller'>View My Auction</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_admin_new_dealer(dealer_name, contact_name, email, license, city, state):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":"navinbhavanimaheshpython@gmail.com","subject":f"New Dealer Registration: {dealer_name}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>New Dealer</h2><p>{dealer_name} | {contact_name} | {email} | {license} | {city}, {state}</p></div>"})
    except Exception as e:
        print(f"Admin email error: {e}")

def send_admin_new_seller(name, email, phone):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":"navinbhavanimaheshpython@gmail.com","subject":f"New Seller Registration: {email}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>New Seller</h2><p>{name} | {email} | {phone}</p></div>"})
    except Exception as e:
        print(f"Admin email error: {e}")

def send_password_reset(email, name, token):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":email,"subject":"Reset Your PrivaBuy Password","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Reset Your Password</h2><p>Hi {name}, click below to reset your password. Expires in 1 hour.</p><a href='https://privabuy.com/reset-password?token={token}'>Reset Password</a></div>"})
    except Exception as e:
        print(f"Reset email error: {e}")

def send_dealer_bid_accepted(dealer_email, dealer_name, year, make, model, amount):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":dealer_email,"subject":f"You Won! {year} {make} {model} - Pay $600 to Proceed","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Your bid was accepted!</h2><p>Congratulations {dealer_name} - pay your $600 platform fee within 24 hours or your bid will be forfeited.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>Pay $600 Now</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_bid_accepted_confirmation(seller_email, seller_name, year, make, model, amount):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Offer Accepted - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>You accepted an offer!</h2><p>Hi {seller_name}, you accepted ${amount:,.0f} for your {year} {make} {model}. The dealer has 24 hours to pay.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_dealer_paid_fee(seller_email, seller_name, year, make, model):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Dealer Paid - Sign Bill of Sale for {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Dealer paid their fee!</h2><p>Hi {seller_name}, the dealer paid their $600 fee. Please sign the Bill of Sale.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>Sign Bill of Sale</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_dealer_seller_signed_bos(dealer_email, dealer_name, year, make, model):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":dealer_email,"subject":f"Seller Signed Bill of Sale - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Seller signed the Bill of Sale</h2><p>Hi {dealer_name}, please sign yours to proceed.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>Sign Now</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_dealer_signed_bos(seller_email, seller_name, year, make, model):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Dealer Signed Bill of Sale - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Both parties signed!</h2><p>Hi {seller_name}, pickup scheduling will begin shortly.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_pickup_slots_proposed(seller_email, seller_name, year, make, model, slot_1, slot_2, slot_3):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Dealer Proposed Pickup Times - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Pickup times proposed</h2><p>Hi {seller_name}:<br><strong>Option 1:</strong> {slot_1}<br><strong>Option 2:</strong> {slot_2}<br><strong>Option 3:</strong> {slot_3}</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>Choose a Time</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_dealer_pickup_confirmed(dealer_email, dealer_name, year, make, model, pickup_time):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":dealer_email,"subject":f"Pickup Confirmed - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Pickup confirmed!</h2><p>Hi {dealer_name}, pickup is confirmed for <strong>{pickup_time}</strong>. After pickup confirm vehicle condition in Deal Flow.</p><a href='https://privabuy.com/app?role=dealer' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_pickup_confirmed(seller_email, seller_name, year, make, model, pickup_time):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Pickup Confirmed - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Pickup locked in!</h2><p>Hi {seller_name}, pickup is confirmed for <strong>{pickup_time}</strong>. Have your title ready.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>View Deal Flow</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_vehicle_confirmed(seller_email, seller_name, year, make, model, amount):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Dealer Confirmed Vehicle - Confirm Payment for {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Dealer confirmed the vehicle!</h2><p>Hi {seller_name}, please confirm when you receive payment of <strong>${amount:,.0f}</strong>.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>Confirm Payment Received</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_seller_payment_confirmed_complete(seller_email, seller_name, year, make, model):
    try:
        resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":seller_email,"subject":f"Last Step - Pay Your $250 PrivaBuy Fee for {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Almost done!</h2><p>Hi {seller_name}, payment confirmed. Pay your $250 PrivaBuy fee to complete.</p><a href='https://privabuy.com/app?role=seller' style='background:#7c5cbf;color:#fff;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;'>Pay $250 Fee</a></div>"})
    except Exception as e:
        print(f"Email error: {e}")

def send_deal_complete(seller_email, seller_name, dealer_email, dealer_name, year, make, model, amount):
    for email, name in [(seller_email, seller_name), (dealer_email, dealer_name)]:
        try:
            resend.Emails.send({"from":"PrivaBuy <notifications@privabuy.com>","to":email,"subject":f"Deal Complete - {year} {make} {model}","html":f"<div style='font-family:Arial,sans-serif;padding:20px;'><h2>Deal complete!</h2><p>Hi {name}, the sale of the {year} {make} {model} for ${amount:,.0f} is fully complete. Thank you for using PrivaBuy!</p></div>"})
        except Exception as e:
            print(f"Email error: {e}")