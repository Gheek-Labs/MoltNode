# Minima Node Web Dashboard

Reference dashboard implementation showing the correct 3-balance display pattern.

## Balance Display (Best Practice)

| Position | Field | Meaning |
|----------|-------|---------|
| **Primary** (large, highlighted) | `sendable` | Available to spend right now |
| **Secondary** | `confirmed` | Full wallet balance (includes locked) |
| **Tertiary** | `unconfirmed` | Pending incoming |

**Never display `total` as a balance** — it is the token's maximum supply (~1 billion for Minima), not your wallet balance. The integration kit hides `total` under `supply.total` to prevent accidental misuse.

## Tooltip

The dashboard includes an info tooltip:
> "Confirmed includes locked funds. Sendable is spendable now."

## Setup

```bash
# From project root
cd templates/node-web-dashboard
npm init -y
npm install express

# Run
node server.js
# Open http://localhost:3000
```

## Architecture

```
server.js           # Express API proxying Minima RPC
public/
  index.html        # Dashboard with 3-balance display
  style.css         # Dark theme styling
```

The server uses `../../integration/node/minima-client.js` which normalizes all responses and moves `total` to `supply.total`.

## API Endpoints

| Endpoint | Returns |
|----------|---------|
| `GET /api/balance` | Normalized balances (no top-level `total`) |
| `GET /api/status` | Parsed node status |
| `GET /api/contacts` | Maxima contacts |
| `GET /api/address` | Receiving address |
