# On-Chain Data Records

Post arbitrary data to the Minima blockchain permanently. Returns a `txpowid` — the on-chain proof.

**Related:** [COMMANDS.md](COMMANDS.md) | [RESPONSE_SCHEMAS.md](RESPONSE_SCHEMAS.md) | [KISSVM.md](KISSVM.md)

---

## AGENT WARNING — hash ≠ on-chain record

| Operation | What it does | Returns | On-chain? |
|-----------|-------------|---------|-----------|
| `hash data:hello` | Local Keccak-256 hash | `{ hash: "0x..." }` | **NO** — purely local, no txpowid |
| `record_data.sh --data "hello"` | Self-send with state data | `{ txpowid: "0x..." }` | **YES** — permanent on-chain record |

**The `hash` command does NOT write anything to the blockchain.** It computes a local hash. To create an on-chain record, you must post a transaction with your data embedded as state variables.

**The explorer link uses `txpowid`, not the hash output.** You cannot look up a `hash` result on the explorer — only `txpowid` values from actual transactions.

---

## How It Works

Minima transactions carry **state variables** (port 0–255) that are stored on-chain permanently. The recipe:

1. Hash your data locally (optional but recommended for large data)
2. Self-send a tiny amount (0.000000001 Minima) with your data in state variables
3. The transaction's `txpowid` is your permanent on-chain proof
4. Look it up: `https://explorer.minima.global/transactions/<txpowid>`

### State Variable Layout

| Port | Purpose | Example |
|------|---------|---------|
| 0 | Data hash or raw data | `0x3a7b...` (must be 0x-prefixed for txnstate) |
| 1 | Label / description | `0x` + hex-encoded label |
| 2 | Timestamp (hex-encoded) | `0x` + hex-encoded ISO 8601 |
| 3+ | Additional metadata | Any 0x-prefixed hex value |

---

## Method 1: Simple (send with state)

The `send` command supports a `state:{}` JSON parameter for quick data records:

```bash
./minima/cli.sh "send address:$(./minima/cli.sh getaddress | jq -r '.response.miniaddress') amount:0.000000001 state:{\"0\":\"mydata\",\"1\":\"label\"}"
```

The SDK `record_onchain()` / `recordOnChain()` methods use this approach internally.

---

## Method 2: Transaction Builder (full control)

For advanced use cases (custom scripts, burn amounts, multi-step builds), use the transaction builder pipeline:

### Step-by-step recipe

```bash
# 1. Create a named transaction
./minima/cli.sh "txncreate id:myrecord"

# 2. Add state variables (data to record)
#    WARNING: txnstate only accepts 0x-prefixed hex values or numbers.
#    Plain strings cause NumberFormatException.
./minima/cli.sh "txnstate id:myrecord port:0 value:0xABCD1234"
./minima/cli.sh "txnstate id:myrecord port:1 value:0x6D796C6162656C"

# 3. Add an output coin with storestate:true (preserves state on-chain)
#    Send to your own address, minimum amount
ADDRESS=$(./minima/cli.sh getaddress | jq -r '.response.miniaddress')
./minima/cli.sh "txnoutput id:myrecord amount:0.000000001 address:${ADDRESS} storestate:true"

# 4. Auto-sign (selects inputs, sets MMR proofs, signs, and posts)
./minima/cli.sh "txnsign id:myrecord publickey:auto txnpostauto:true txndelete:true"
```

The `txnsign` with `txnpostauto:true` automatically:
- Selects input coins to fund the transaction
- Sets MMR proofs and scripts
- Signs the transaction
- Posts it to the network
- `txndelete:true` cleans up the named transaction after posting

### Alternative: Separate sign and post

```bash
# Sign without auto-posting
./minima/cli.sh "txnsign id:myrecord publickey:auto"

# Manually add inputs for funding
./minima/cli.sh "txnaddamount id:myrecord amount:0.000000001"

# Set scripts and MMR proofs
./minima/cli.sh "txnbasics id:myrecord"

# Post with optional burn and mine flags
./minima/cli.sh "txnpost id:myrecord auto:true burn:0 mine:true"

# Clean up
./minima/cli.sh "txndelete id:myrecord"
```

### txnstate value format

> **CRITICAL:** `txnstate` only accepts **0x-prefixed hex values** or **numbers**.
> Plain text strings like `hello` cause `NumberFormatException`.
>
> To record text, first hash it or hex-encode it:
> ```bash
> # Hash the text (returns hex)
> HASH=$(./minima/cli.sh "hash data:hello" | jq -r '.response.hash')
> ./minima/cli.sh "txnstate id:myrecord port:0 value:${HASH}"
>
> # Or hex-encode manually (Python example):
> HEX="0x$(echo -n 'hello' | xxd -p)"
> ./minima/cli.sh "txnstate id:myrecord port:0 value:${HEX}"
> ```
>
> The `send ... state:{...}` method (Method 1) accepts plain strings in the JSON — it handles encoding internally.

### Mining and Confirmation Strategy

| Parameter | Effect |
|-----------|--------|
| `mine:true` on `txnpost` | Mine the transaction immediately (does local proof-of-work) |
| `burn:N` on `txnpost` | Attach N Minima as a burn fee (incentivizes faster inclusion) |
| No burn, no mine | Transaction goes to mempool, included when a block is found |

For most use cases, the default (no burn, no mine) is fine — transactions are typically included within a few blocks. Use `mine:true` when you need immediate local proof-of-work, or `burn:N` to incentivize faster network-wide inclusion.

---

## Shell Script

```bash
# Record data on-chain (simple mode using send)
./minima/record_data.sh --data "hello world"

# Record with a label
./minima/record_data.sh --data "hello world" --port 1

# Record a pre-computed hash
./minima/record_data.sh --data "0x3a7b2c..."

# Record with burn fee for faster confirmation
./minima/record_data.sh --data "0xABCD" --burn 0.001

# Record with immediate mining
./minima/record_data.sh --data "0xABCD" --mine
```

Output:
```json
{
  "txpowid": "0x1234abcd...",
  "explorer": "https://explorer.minima.global/transactions/0x1234abcd...",
  "data": "hello world",
  "port": 0,
  "timestamp": "2026-02-20T12:00:00Z"
}
```

---

## SDK Usage

### Python

```python
from minima_client import MinimaClient

client = MinimaClient()

# Record data on-chain (port 0 by default)
result = client.record_onchain("hello world", label="my-document")
print(result['txpowid'])       # 0x1234abcd...
print(result['explorer_url'])  # https://explorer.minima.global/transactions/0x1234abcd...

# Record on a specific port with burn
result = client.record_onchain("0xABCD", port=3, burn="0.001")

# Record a pre-computed hash
h = client.hash("large document content")
result = client.record_onchain(h['hash'], label="doc-hash")
```

### Node.js

```javascript
import { MinimaClient } from './minima-client.js';

const client = new MinimaClient();

// Record data on-chain (port 0 by default)
const result = await client.recordOnChain('hello world', { label: 'my-document' });
console.log(result.txpowid);      // 0x1234abcd...
console.log(result.explorerUrl);   // https://explorer.minima.global/transactions/0x1234abcd...

// Record on a specific port with burn
const result2 = await client.recordOnChain('0xABCD', { port: 3, burn: '0.001' });

// Record a pre-computed hash
const h = await client.hash('large document content');
const result3 = await client.recordOnChain(h.hash, { label: 'doc-hash' });
```

---

## Common Mistakes

### 1. Using `hash` thinking it records on-chain

```python
# WRONG — this is purely local, nothing goes on-chain
result = client.hash("my data")
# result has no txpowid, no explorer link

# RIGHT — this posts to the blockchain
result = client.record_onchain("my data")
# result has txpowid and explorer_url
```

### 2. Using hash output as explorer link

```python
# WRONG — hash output is not a txpowid
h = client.hash("data")
url = f"https://explorer.minima.global/transactions/{h['hash']}"  # 404!

# RIGHT — use txpowid from an actual transaction
result = client.record_onchain("data")
url = result['explorer_url']  # works
```

### 3. Plain strings in txnstate

```bash
# WRONG — causes NumberFormatException
./minima/cli.sh "txnstate id:myrecord port:0 value:hello"

# RIGHT — hex-encode or hash first
HASH=$(./minima/cli.sh "hash data:hello" | jq -r '.response.hash')
./minima/cli.sh "txnstate id:myrecord port:0 value:${HASH}"
```

### 4. Sending too much for a record

```python
# WRONG — wastes funds
client.send(my_address, 100, ...)  # don't need 100 Minima to record data

# RIGHT — record_onchain uses minimum amount (0.000000001)
client.record_onchain("data")
```

### 5. Forgetting storestate:true

```bash
# WRONG — state variables not preserved in output coin
./minima/cli.sh "txnoutput id:myrecord amount:0.000000001 address:${ADDR}"

# RIGHT — storestate:true preserves state on the coin
./minima/cli.sh "txnoutput id:myrecord amount:0.000000001 address:${ADDR} storestate:true"
```

---

## Verification

To verify a record exists on-chain:

```bash
# By txpowid
./minima/cli.sh "txpow txpowid:0x1234abcd..."

# The state variables in the response contain your data
# Look for body.txn.state[0], state[1], etc.
```

---

## Cost

Each on-chain record costs **0.000000001 Minima** (one billionth). This is the minimum transaction amount. At current supply, this is effectively free for reasonable usage. Optional `burn` adds a priority fee.

---

## Advanced: Custom Scripts

For data records that enforce access controls or conditions, combine state variables with KISSVM scripts. See [KISSVM.md](KISSVM.md) for the full language reference.

Example: Time-locked data record (only readable after block 2000000):
```bash
./minima/cli.sh "txncreate id:timelocked"
./minima/cli.sh "txnstate id:timelocked port:0 value:0xMYDATA"
./minima/cli.sh "txnoutput id:timelocked amount:0.000000001 address:$(./minima/cli.sh 'scripts action:addscript script:[IF @BLOCK GTE 2000000 THEN RETURN SIGNEDBY(0xMYKEY) ENDIF RETURN FALSE]' | jq -r '.response.address') storestate:true"
./minima/cli.sh "txnsign id:timelocked publickey:auto txnpostauto:true txndelete:true"
```

---

## Flow Diagram

```
Your Data
    │
    ▼
hash (optional) ──→ local hash (NOT on-chain)
    │
    ▼ (hex-encoded data or hash)
    │
    ├──→ Method 1: send ... state:{...}          ──→ txpowid
    │         (simple, handles encoding)
    │
    └──→ Method 2: txncreate → txnstate → txnoutput storestate:true → txnsign txnpostauto:true
              (full control, custom scripts)       ──→ txpowid
    │
    ▼
Verify: txpow txpowid:0x...
Explorer: https://explorer.minima.global/transactions/<txpowid>
```
