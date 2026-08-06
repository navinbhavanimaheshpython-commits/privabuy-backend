// register_bill_webhook.js
//
// Node.js port of register_bill_webhook.py — no dependencies needed
// (uses the built-in fetch available in Node 18+).
//
// Usage:
//   node register_bill_webhook.js <notification_url>
//
// Requires these environment variables to be set first:
//   BILL_DEV_KEY
//   BILL_USERNAME
//   BILL_PASSWORD
//   BILL_ORG_ID
//   BILL_API_BASE (optional, defaults to the STAGE gateway)

const BILL_LOGIN_BASE = process.env.BILL_LOGIN_BASE || "https://gateway.stage.bill.com/connect/v3";
const BILL_EVENTS_BASE = process.env.BILL_EVENTS_BASE || "https://gateway.stage.bill.com/connect-events/v3";

function requireEnv(name) {
  const val = process.env[name];
  if (!val) {
    console.error(`Missing required environment variable: ${name}`);
    process.exit(1);
  }
  return val;
}

const BILL_DEV_KEY = requireEnv("BILL_DEV_KEY");
const BILL_USERNAME = requireEnv("BILL_USERNAME");
const BILL_PASSWORD = requireEnv("BILL_PASSWORD");
const BILL_ORG_ID = requireEnv("BILL_ORG_ID");

async function login() {
  const res = await fetch(`${BILL_LOGIN_BASE}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: BILL_USERNAME,
      password: BILL_PASSWORD,
      organizationId: BILL_ORG_ID,
      devKey: BILL_DEV_KEY,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Login failed: ${res.status} ${res.statusText}\n${text}`);
  }

  const data = await res.json();
  return data.sessionId;
}

function uuid4() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

async function registerWebhook(sessionId, notificationUrl) {
  const res = await fetch(`${BILL_EVENTS_BASE}/subscriptions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Idempotent-Key": uuid4(),
      devKey: BILL_DEV_KEY,
      sessionId: sessionId,
    },
    body: JSON.stringify({
      name: "PrivaBuy payment webhook",
      status: { enabled: true },
      events: [
        { type: "invoice.updated", version: "1" },
        { type: "bill.updated", version: "1" },
      ],
      notificationUrl: notificationUrl,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Subscription creation failed: ${res.status} ${res.statusText}\n${text}`);
  }

  return res.json();
}

async function main() {
  const notificationUrl = process.argv[2];
  if (!notificationUrl) {
    console.error("Usage: node register_bill_webhook.js <notification_url>");
    process.exit(1);
  }

  try {
    const sessionId = await login();
    const result = await registerWebhook(sessionId, notificationUrl);

    console.log("Subscription created:");
    console.log(result);
    console.log();

    if (result.securityKey) {
      console.log(
        `SECURITY KEY (save this now — set as BILL_WEBHOOK_SECURITY_KEY in Railway):\n${result.securityKey}`
      );
    } else {
      console.log(
        "No securityKey found in response — check BILL's subscription API docs, " +
          "the field name may differ from what this script expects."
      );
    }
  } catch (err) {
    console.error("Error:", err.message);
    if (err.cause) {
      console.error("Underlying cause:", err.cause);
    }
    console.error("\nDebug info:");
    console.error("  BILL_LOGIN_BASE:", BILL_LOGIN_BASE);
    console.error("  BILL_EVENTS_BASE:", BILL_EVENTS_BASE);
    console.error("  BILL_USERNAME set:", !!BILL_USERNAME);
    console.error("  BILL_DEV_KEY set:", !!BILL_DEV_KEY);
    console.error("  BILL_ORG_ID set:", !!BILL_ORG_ID);
    process.exit(1);
  }
}

main();