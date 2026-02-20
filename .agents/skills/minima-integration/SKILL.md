---
name: minima-integration
description: Integrate with the local Minima blockchain node. Use when building apps that query balance, send transactions, post on-chain records, or listen for block events via webhooks.
---

# Minima Node Integration

This repo runs a headless Minima blockchain node with RPC enabled. Use the SDKs in `integration/` — never raw `http.get()`.

## 1. Ports & Endpoints

| Port | Protocol | Purpose | Access |
|------|----------|---------|--------|
| 9005 | HTTP | **RPC API** — all commands | Local only (`localhost`) |
| 9001 | TCP | P2P network (peer sync) | Open |
| 9003 | HTTPS | MDS (MiniDapp System) | Password-protected, SSL |

RPC URL: `http://localhost:9005/<url-encoded-command>`

```bash
curl http://localhost:9005/status
curl "http://localhost:9005/send%20address:MxG08..%20amount:1"
```

## 2. LF-Only HTTP Responses (Critical)

Minima RPC returns bare JSON with **LF-only** line endings (`\n`, no `\r`).

**Problem:** Node.js `http.get()` and some HTTP parsers expect `\r\n` (CRLF) and will return garbled or incomplete data.

**Fix:** Use the SDK clients — they handle this automatically via `fetch()`:

```javascript
// WRONG — may fail with LF-only responses
import http from 'node:http';
http.get('http://localhost:9005/status', ...);

// CORRECT — use the SDK
import { MinimaClient } from './integration/node/minima-client.js';
const client = new MinimaClient();
const status = await client.status();
```

If you must use raw HTTP, use `fetch()` (global in Node 18+) or read until connection close, never until `\r\n\r\n`.

## 3. SDK Usage

### Node.js

```javascript
import { MinimaClient } from './integration/node/minima-client.js';

const client = new MinimaClient(); // default: localhost:9005

const status = await client.status();        // chain info
const bal    = await client.balance();        // normalized balances
const nfts   = await client.nfts();           // NFTs (decimals=0)
const addr   = await client.getaddress();     // receive address
const tx     = await client.send('MxG08...', 1); // send Minima

// Raw RPC
const result = await client.command('tokens');
```

### Python

```python
from integration.python.minima_client import MinimaClient

client = MinimaClient()  # default: localhost:9005

status = client.status()          # chain info
bal    = client.balance()         # normalized balances
nfts   = client.nfts()            # NFTs (decimals=0)
addr   = client.getaddress()      # receive address
tx     = client.send("MxG08...", 1)  # send Minima

# Raw RPC
result = client.command("tokens")
```

### Shell (via cli.sh)

```bash
./minima/cli.sh status
./minima/cli.sh balance
./minima/cli.sh "send address:MxG08... amount:1"
```

## 4. Response Format & Schemas

All RPC responses follow this envelope:

```json
{
  "status": true,
  "pending": false,
  "response": { ... }
}
```

- `status: false` → command failed; check `error` field
- `pending: true` → async operation; poll for result
- Numeric fields are **mixed types**: some are integers (e.g., `block`, `size`), others are strings (e.g., `nonce`, `total`). Use the SDK's safe parsers.

**Schema reference:** `minima/RESPONSE_SCHEMAS.md` (human-readable) and `minima/rpc/schemas/*.schema.json` (machine-readable) cover all 25 commands.

## 5. Balance Semantics — READ THIS

> **`total` is NOT the wallet balance.** It is the token's max supply (~1 billion for Minima). Displaying `total` as balance is the #1 integration mistake.

| Field | Meaning | Display as |
|-------|---------|-----------|
| **`sendable`** | Spendable right now | **Primary balance** |
| `confirmed` | Full wallet (includes locked) | Full balance |
| `unconfirmed` | Pending incoming | Pending indicator |
| `coins` | Number of UTXOs | Coin count |
| `total` | Token max supply / hardcap | **NEVER display as balance** |

The SDKs' `balance()` method returns normalized objects with these fields. Always use `sendable` for "your balance":

```javascript
const bal = await client.balance();
console.log(`Balance: ${bal[0].sendable} ${bal[0].token}`);
// Balance: 0.5 Minima
```

## 6. On-Chain Records

Post permanent data on-chain using the transaction builder pipeline.

### Quick way (shell)

```bash
./minima/record_data.sh --data "sensor:42,ts:1700000000"
./minima/record_data.sh --data "event:alert" --port 100 --burn 0.01
./minima/record_data.sh --data "log:critical" --mine
```

### SDK way

```javascript
const result = await client.recordOnChain('sensor:42,ts:1700000000');
// result.txpowid = "0x..."
// result.explorer = "https://..."

// With custom port and burn
const result2 = await client.recordOnChain('event:alert', { port: 100, burn: 0.01 });
```

```python
result = client.record_onchain("sensor:42,ts:1700000000")
# result["txpowid"] = "0x..."

result2 = client.record_onchain("event:alert", port=100, burn=0.01)
```

### Transaction builder recipe (advanced)

```bash
./minima/cli.sh "txncreate id:myrecord"
./minima/cli.sh "txnstate id:myrecord port:0 value:0x$(echo -n 'my data' | xxd -p)"
./minima/cli.sh "txnstate id:myrecord port:255 value:$(date +%s)"
./minima/cli.sh "txnoutput id:myrecord storestate:true amount:0.000000001 address:$(./minima/cli.sh getaddress | jq -r '.response.miniaddress')"
./minima/cli.sh "txnsign id:myrecord publickey:auto"
./minima/cli.sh "txnpost id:myrecord txnpostauto:true"
```

**Caveat:** `txnstate` only accepts `0x`-prefixed hex values or numbers. Plain strings cause `NumberFormatException`. Always hex-encode text data.

See `minima/ONCHAIN_RECORDS.md` for the full recipe and `minima/KISSVM.md` for the scripting language reference.

## 7. Webhooks

The node can POST JSON events to your HTTP endpoint.

### Register

```bash
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/events"
./minima/cli.sh "webhooks action:add hook:http://127.0.0.1:8099/blocks filter:NEWBLOCK"
```

### Event types

| Event | Frequency | Description |
|-------|-----------|-------------|
| `NEWBLOCK` | ~50s | New block accepted |
| `MINING` | ~50s | Mining attempt started |
| `MDS_TIMER_10SECONDS` | 10s | Heartbeat |
| `MDS_TIMER_60SECONDS` | 60s | Slow heartbeat |
| `NEWTRANSACTION` | On activity | Wallet-relevant transaction |
| `NEWBALANCE` | On activity | Balance changed |

### Payload envelope

```json
{
  "event": "NEWBLOCK",
  "data": {
    "txpow": {
      "txpowid": "0x00000009BECE...",
      "isblock": true,
      "header": { "block": "1958782", "timemilli": "1771591684185" },
      "body": { "txnlist": [] }
    }
  }
}
```

### Behavior

- POST only, JSON body
- No retry — events are lost if your endpoint is down
- Not persistent — webhooks clear on node restart, re-register on boot
- Listed hooks have `#` prefix (e.g., `#http://...`) — remove without the `#`

Reference template: `templates/node-webhook-listener/server.js` (zero-dependency Node.js listener).

Full docs: `minima/WEBHOOKS.md`

## 8. Common Errors

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ECONNREFUSED` on port 9005 | Node not running | Start via `./minima/start.sh` or restart the Minima Node workflow |
| `status: false` with `error` string | Bad command or params | Check `minima/COMMANDS.md` for correct syntax |
| `pending: true` in response | Async operation in progress | Poll `status` or wait; operation will complete in background |
| `NumberFormatException` in txnstate | Non-hex string value | Prefix with `0x` or hex-encode: `0x$(echo -n 'text' | xxd -p)` |
| Garbled/incomplete JSON from Node.js `http` | LF-only line endings | Use the SDK client or `fetch()` instead of `http.get()` |
| Balance shows ~1 billion | Displaying `total` field | Use `sendable` field instead — `total` is token max supply |
| Webhook not firing | Node restarted or endpoint down | Re-register webhooks after every node restart; verify endpoint is reachable |
| `MinimaError` from SDK | RPC returned `status: false` | Check `error` message; common: invalid address, insufficient balance |
| `MinimaConnectionError` from SDK | Node unreachable after retries | Verify node is running: `curl http://localhost:9005/status` |

## File Reference

| Path | Purpose |
|------|---------|
| `integration/node/minima-client.js` | Node.js SDK (ESM, JSDoc typed) |
| `integration/python/minima_client.py` | Python SDK |
| `minima/cli.sh` | Shell CLI wrapper |
| `minima/record_data.sh` | On-chain data posting script |
| `minima/COMMANDS.md` | Full RPC command reference |
| `minima/RESPONSE_SCHEMAS.md` | Response field semantics (25 commands) |
| `minima/rpc/schemas/*.schema.json` | Machine-readable JSON schemas |
| `minima/WEBHOOKS.md` | Webhook event catalog |
| `minima/ONCHAIN_RECORDS.md` | Transaction builder recipe |
| `minima/KISSVM.md` | KISSVM scripting language glossary |
| `minima/AGENT_QUICKSTART.md` | Agent operations guide |
| `templates/node-webhook-listener/` | Webhook listener reference |
