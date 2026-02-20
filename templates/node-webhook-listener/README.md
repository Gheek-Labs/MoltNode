# Minima Webhook Listener

Reference Express-free Node.js server that receives Minima webhook events.

## Setup

```bash
cd templates/node-webhook-listener
node server.js
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LISTEN_PORT` | `8099` | Port for the webhook listener |
| `MINIMA_RPC` | `http://127.0.0.1:9005` | Minima node RPC URL |
| `WEBHOOK_FILTER` | (none) | Event filter (e.g., `NEWBLOCK`, `MINING`) |

## How It Works

1. Starts an HTTP server on `LISTEN_PORT`
2. Registers itself as a webhook with the Minima node
3. Receives POST events at `/events`
4. Logs each event with type-specific formatting
5. Exposes `/status` endpoint with event counts and last block height
6. Cleans up webhook registration on shutdown (SIGINT)

## Event Types

- `NEWBLOCK` — New block accepted (logs height, superblock level, tx count)
- `MINING` — Mining attempt started
- `MDS_TIMER_10SECONDS` — 10-second heartbeat
- `MDS_TIMER_60SECONDS` — 60-second heartbeat
- `NEWTRANSACTION` — Wallet-relevant transaction
- `NEWBALANCE` — Balance change
- `MAXIMA` — Maxima message received

## Filtering

Only receive specific events:

```bash
WEBHOOK_FILTER=NEWBLOCK node server.js
```

## Dependencies

None — uses only Node.js built-in `http` module and global `fetch`.

## See Also

- [WEBHOOKS.md](../../minima/WEBHOOKS.md) — Full webhook documentation
- [RESPONSE_SCHEMAS.md](../../minima/RESPONSE_SCHEMAS.md) — TxPoW field reference
