"""
Manual end-to-end test for referral_logic.py

Run against a throwaway Postgres (NOT your Railway prod DB):

    docker run --name privabuy-test -e POSTGRES_PASSWORD=test -p 5432:5432 -d postgres

Then:
    pip install psycopg2-binary --break-system-packages
    python test_referral_logic.py

This creates a minimal sellers/cars table, runs the full referral flow,
and prints assertions so you can see the cap and fraud logic fire.
"""

import psycopg2
from referral_logic import (
    SCHEMA_SQL,
    generate_referral_code,
    record_referral_on_signup,
    qualify_referral_if_eligible,
    get_available_credit,
    apply_referral_credit,
    check_fraud_signals,
    review_flagged_credit,
    MAX_REFERRALS,
    MAX_CREDIT,
)

DB_URL = "postgresql://postgres:test@127.0.0.1:5432/postgres"


def setup(cur):
    # Minimal stand-ins for your real tables — enough for the referral
    # module's foreign keys to work. Delete/replace with your real schema.
    cur.execute("DROP TABLE IF EXISTS referral_credits CASCADE")
    cur.execute("DROP TABLE IF EXISTS cars CASCADE")
    cur.execute("DROP TABLE IF EXISTS sellers CASCADE")
    cur.execute("""
        CREATE TABLE sellers (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100),
            referral_code VARCHAR(12) UNIQUE,
            referred_by_code VARCHAR(12),
            signup_ip VARCHAR(45),
            stripe_card_fingerprint VARCHAR(64)
        )
    """)
    cur.execute("""
        CREATE TABLE cars (
            car_id SERIAL PRIMARY KEY,
            seller_id INTEGER REFERENCES sellers(id)
        )
    """)
    cur.execute(SCHEMA_SQL)


def make_seller(cur, email):
    cur.execute("INSERT INTO sellers (email) VALUES (%s) RETURNING id", (email,))
    return cur.fetchone()[0]


def make_car(cur, seller_id):
    cur.execute("INSERT INTO cars (seller_id) VALUES (%s) RETURNING car_id", (seller_id,))
    return cur.fetchone()[0]


def run():
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("=== Setting up schema ===")
    setup(cur)

    # --- Scenario 1: normal referral flow, one referral qualifies ---
    print("\n=== Scenario 1: single legit referral ===")
    referrer = make_seller(cur, "referrer@test.com")
    code = generate_referral_code(cur, referrer)
    print(f"Referrer code: {code}")

    friend = make_seller(cur, "friend@test.com")
    record_referral_on_signup(cur, friend, code, signup_ip="1.1.1.1")

    car = make_car(cur, friend)
    qualify_referral_if_eligible(cur, friend, car)

    credit = get_available_credit(cur, referrer)
    print(f"Available credit after 1 referral: ${credit}")
    assert credit == 25, f"expected 25, got {credit}"

    # --- Scenario 2: push past the 4-referral cap ---
    print("\n=== Scenario 2: 5 referrals, cap at 4 / $100 ===")
    for i in range(4):  # 4 more, bringing total attempted to 5
        ref = make_seller(cur, f"ref{i}@test.com")
        record_referral_on_signup(cur, ref, code, signup_ip=f"2.2.2.{i}")
        c = make_car(cur, ref)
        qualify_referral_if_eligible(cur, ref, c)

    credit = get_available_credit(cur, referrer)
    print(f"Available credit after 5 total referrals: ${credit} (cap is ${MAX_CREDIT})")
    assert credit == MAX_CREDIT, f"expected cap {MAX_CREDIT}, got {credit}"

    cur.execute("SELECT status, COUNT(*) FROM referral_credits WHERE referrer_id=%s GROUP BY status", (referrer,))
    print("Status breakdown:", cur.fetchall())

    # --- Scenario 3: fee application ---
    print("\n=== Scenario 3: applying credit to the $350 fee ===")
    result = apply_referral_credit(cur, referrer, base_fee=350)
    print(result)
    assert result["final_fee"] == 250, f"expected 250, got {result['final_fee']}"

    # --- Scenario 4: fraud - same card fingerprint ---
    print("\n=== Scenario 4: same card fingerprint gets flagged ===")
    fraud_referrer = make_seller(cur, "fraud_referrer@test.com")
    fraud_code = generate_referral_code(cur, fraud_referrer)
    cur.execute("UPDATE sellers SET stripe_card_fingerprint='CARD_ABC' WHERE id=%s", (fraud_referrer,))

    fake_alt = make_seller(cur, "fraud_alt@test.com")
    record_referral_on_signup(cur, fake_alt, fraud_code, signup_ip="9.9.9.9")
    cur.execute("UPDATE sellers SET stripe_card_fingerprint='CARD_ABC' WHERE id=%s", (fake_alt,))

    flags = check_fraud_signals(cur, fraud_referrer, fake_alt)
    print("Fraud flags detected:", flags)
    assert "same_card_fingerprint" in flags

    car2 = make_car(cur, fake_alt)
    qualify_referral_if_eligible(cur, fake_alt, car2)

    cur.execute("SELECT status, flag_reason FROM referral_credits WHERE referrer_id=%s AND referred_id=%s",
                (fraud_referrer, fake_alt))
    status, reason = cur.fetchone()
    print(f"Credit status: {status}, reason: {reason}")
    assert status == "flagged_review"

    credit = get_available_credit(cur, fraud_referrer)
    print(f"Available credit before review (should be 0): ${credit}")
    assert credit == 0

    # --- Scenario 5: admin approves the flagged credit ---
    print("\n=== Scenario 5: admin manually approves it ===")
    cur.execute("SELECT id FROM referral_credits WHERE referrer_id=%s AND referred_id=%s",
                (fraud_referrer, fake_alt))
    credit_id = cur.fetchone()[0]
    review_flagged_credit(cur, credit_id, approve=True, reviewer="navin@privabuy.com")

    credit = get_available_credit(cur, fraud_referrer)
    print(f"Available credit after admin approval: ${credit}")
    assert credit == 25

    print("\n=== ALL SCENARIOS PASSED ===")
    cur.close()
    conn.close()


if __name__ == "__main__":
    run()