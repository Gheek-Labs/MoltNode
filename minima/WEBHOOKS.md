# Minima Webhooks

Push notifications from your Minima node. The node POSTs JSON to your endpoint whenever events occur — new blocks, mining attempts, timers.

## Quick Start

```bash
# Register a webhook
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/events"

# Register with event filter (only NEWBLOCK events)
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/events filter:NEWBLOCK"

# List registered webhooks
./minima/cli.sh "webhooks action:list"

# Remove a webhook
./minima/cli.sh "webhooks action:remove hook:http://127.0.0.1:8099/events"

# Clear all webhooks
./minima/cli.sh "webhooks action:clear"
```

## RPC Syntax

```
webhooks action:list|add|remove|clear hook:<url> filter:<event_type>
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| `action`  | No       | `list` (default), `add`, `remove`, `clear` |
| `hook`    | For add/remove | POST endpoint URL |
| `filter`  | No       | Event type name to filter (e.g., `NEWBLOCK`, `MINING`) |

## Event Types

| Event | Frequency | Description |
|-------|-----------|-------------|
| `NEWBLOCK` | ~every 50s | A new block was added to the chain |
| `MINING` | ~every 50s | Node is mining a new TxPoW candidate |
| `MDS_TIMER_10SECONDS` | Every 10s | Heartbeat timer (MiniDapp polling) |
| `MDS_TIMER_60SECONDS` | Every 60s | Slow heartbeat timer |

### Additional event types (not always present — require activity)

| Event | Trigger | Description |
|-------|---------|-------------|
| `NEWTRANSACTION` | Incoming/outgoing tx | A transaction relevant to this wallet |
| `NEWBALANCE` | Balance change | Wallet balance updated |
| `MAXIMA` | Maxima message | Received a Maxima message |

## Payload Format

All events are delivered as HTTP POST with `Content-Type: application/json`.

Every payload has the same envelope:

```json
{
  "event": "<EVENT_TYPE>",
  "data": { ... }
}
```

### NEWBLOCK

Fired when a new block is accepted into the chain. Contains the full TxPoW object.

```json
{
  "event": "NEWBLOCK",
  "data": {
    "txpow": {
      "txpowid": "0x00000009BECE8444E13194DBFCF997C2...",
      "isblock": true,
      "istransaction": false,
      "superblock": 2,
      "size": 846,
      "burn": 0,
      "header": {
        "chainid": "0x00",
        "block": "1958782",
        "blkdiff": "0x493F420DF2DCA03BD1A1E...",
        "cascadelevels": 32,
        "superparents": [ ... ],
        "magic": {
          "currentmaxtxpowsize": "65536",
          "currentmaxkissvmops": "1024",
          "currentmaxtxn": "256",
          "currentmintxpowwork": "0x068DB8BAC710CB..."
        },
        "mmr": "0xFF9C951D1D35D66CE948...",
        "total": "999979665.550688...",
        "customhash": "0x00",
        "txbodyhash": "0xFBF73E54CD12DB2E...",
        "nonce": "99797668324901354.335...",
        "timemilli": "1771591684185",
        "date": "Fri Feb 20 12:48:04 GMT 2026"
      },
      "hasbody": true,
      "body": {
        "prng": "0x647E312AD5F44F...",
        "txndiff": "0x49487A14F52019BA...",
        "txn": {
          "inputs": [],
          "outputs": [],
          "state": [],
          "linkhash": "0x00",
          "transactionid": "0xDECA2444..."
        },
        "witness": { "signatures": [], "mmrproofs": [], "scripts": [] },
        "burntxn": { "inputs": [], "outputs": [], "state": [], "linkhash": "0x00", "transactionid": "0xDECA2444..." },
        "burnwitness": { "signatures": [], "mmrproofs": [], "scripts": [] },
        "txnlist": []
      }
    }
  }
}
```

**Key fields:**

| Field | Type | Notes |
|-------|------|-------|
| `txpow.txpowid` | string (hex) | Unique block identifier |
| `txpow.isblock` | boolean | Always `true` for NEWBLOCK |
| `txpow.istransaction` | boolean | `true` if block contains a transaction |
| `txpow.superblock` | integer | Superblock level (0 = normal, higher = rarer/heavier) |
| `txpow.size` | integer | TxPoW size in bytes |
| `txpow.burn` | integer | Burn amount (0 if no burn) |
| `header.block` | string | Block height |
| `header.timemilli` | string | Unix timestamp in milliseconds |
| `header.date` | string | Human-readable date |
| `header.cascadelevels` | integer | Cascade depth |
| `body.txnlist` | array | List of transaction IDs included in this block |

### MINING

Fired when the node begins mining a new TxPoW. Structure is identical to NEWBLOCK, plus a `mining` boolean flag.

```json
{
  "event": "MINING",
  "data": {
    "txpow": {
      "txpowid": "0xD3B810338726152940668...",
      "isblock": false,
      "istransaction": false,
      "superblock": -1,
      "size": 754,
      "burn": 0,
      "header": { ... },
      "hasbody": true,
      "body": { ... }
    },
    "mining": true
  }
}
```

**Notes:**
- `superblock: -1` indicates an unmined candidate
- `mining: true` is always present
- `isblock` is `false` because it hasn't been accepted yet
- `txpowid` changes with each mining attempt

### MDS_TIMER_10SECONDS

Heartbeat fired every 10 seconds. Useful for periodic polling or health checks.

```json
{
  "event": "MDS_TIMER_10SECONDS",
  "data": {
    "timemilli": "1771591678571"
  }
}
```

### MDS_TIMER_60SECONDS

Slow heartbeat fired every 60 seconds.

```json
{
  "event": "MDS_TIMER_60SECONDS",
  "data": {
    "timemilli": "1771591704573"
  }
}
```

## Filters

Use the `filter` parameter to only receive specific event types:

```bash
# Only new blocks
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/blocks filter:NEWBLOCK"

# Only mining events
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/mining filter:MINING"
```

You can register multiple webhooks with different filters to route events to different endpoints:

```bash
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/blocks filter:NEWBLOCK"
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/timers filter:MDS_TIMER_60SECONDS"
```

## Webhook Behavior

- **List prefix**: Registered hooks are listed with a `#` prefix (e.g., `#http://127.0.0.1:8099/events`) — this is normal; use the full URL (without `#`) when removing
- **Method**: Always HTTP POST
- **Content-Type**: `application/json`
- **Retry**: No automatic retry — if your endpoint is down, events are lost
- **Order**: Events arrive in chronological order but are not guaranteed to be sequential
- **Persistence**: Webhooks are stored in memory — they are cleared on node restart
- **Re-register**: Your listener should re-register webhooks after node restart

## Polling Fallback

If webhooks are impractical (firewalls, NAT, ephemeral environments), poll the RPC API instead:

```bash
# Poll for new blocks every 30 seconds
while true; do
  ./minima/cli.sh status | jq '.response.chain.block'
  sleep 30
done
```

```javascript
// Node.js polling example
import { MinimaClient } from './minima-client.js';
const client = new MinimaClient();

let lastBlock = 0;
setInterval(async () => {
  const status = await client.status();
  const block = parseInt(status.chain.block);
  if (block > lastBlock) {
    console.log(`New block: ${block}`);
    lastBlock = block;
  }
}, 30000);
```

```python
# Python polling example
import time
from minima_client import MinimaClient

client = MinimaClient()
last_block = 0

while True:
    status = client.status()
    block = int(status["chain"]["block"])
    if block > last_block:
        print(f"New block: {block}")
        last_block = block
    time.sleep(30)
```

## Agent Integration

For agents building on Minima webhooks:

1. **Start a listener** on a local port (e.g., 8099)
2. **Register the webhook** via RPC
3. **Re-register on node restart** — webhooks are not persistent
4. **Use filters** to reduce noise — `NEWBLOCK` and `MDS_TIMER_10SECONDS` are the most common
5. **Handle failures gracefully** — events are fire-and-forget with no retry

### Common patterns

| Use Case | Filter | Notes |
|----------|--------|-------|
| Block explorer | `NEWBLOCK` | Track chain height, extract transactions from `body.txnlist` |
| Balance monitor | (none) | Watch for `NEWBALANCE` events (requires wallet activity) |
| Health check | `MDS_TIMER_10SECONDS` | Alert if timer stops arriving |
| Transaction watch | (none) | Watch for `NEWTRANSACTION` events |
| Mining stats | `MINING` | Track mining attempts and superblock levels |

## See Also

- [COMMANDS.md](COMMANDS.md) — Full RPC command reference
- [RESPONSE_SCHEMAS.md](RESPONSE_SCHEMAS.md) — TxPoW field semantics
- [AGENT_QUICKSTART.md](AGENT_QUICKSTART.md) — Agent operations guide
