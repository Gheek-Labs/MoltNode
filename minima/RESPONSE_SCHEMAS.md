# Minima RPC Response Schemas

Human/agent-readable guide to Minima RPC response formats with semantic annotations and agent warnings.

**Machine-readable schemas:** `minima/rpc/schemas/*.schema.json`

**Full command reference:** [COMMANDS.md](COMMANDS.md)

---

## General Response Format

Every RPC response follows this envelope:

```json
{
  "status": true,        // true = success, false = error
  "response": { ... },   // Command-specific payload (object or array)
  "error": "..."         // Only present when status is false
}
```

> **AGENT WARNING:** Always check `status` before reading `response`. When `status` is `false`, `response` may be absent and `error` will contain the failure reason.

### Global Type Gotchas

- **Numeric strings:** Many numeric fields (`length`, `block`, `amount`, `coins`, `confirmed`, etc.) are returned as **strings**, not numbers. Always parse: `int(x)`, `float(x)`, or `Decimal(x)`.
- **Hex values:** All hashes, addresses, and keys are `0x`-prefixed hex strings.
- **LF line endings:** HTTP responses use `\n` only (no `\r\n`). Use a JSON parser, never regex.

---

## balance

Returns token balances for this node's wallet.

```json
{ "status": true, "response": [{
  "token": "Minima",
  "tokenid": "0x00",
  "confirmed": "1000",
  "unconfirmed": "0",
  "sendable": "1000",
  "coins": "3",
  "total": "1000000000"
}]}
```

| Field | Type | Meaning |
|-------|------|---------|
| `token` | string | Token display name |
| `tokenid` | string | Token ID. `0x00` = native Minima |
| `confirmed` | string | Full wallet balance (includes locked coins) |
| `unconfirmed` | string | Received but pending confirmation |
| `sendable` | string | **Available to spend** (confirmed minus locked) |
| `coins` | string | Number of UTXO coins for this token |
| `total` | string | **TOKEN MAX SUPPLY / HARDCAP** |

> **AGENT WARNING — `total` is a trap:**
> `total` is the token's maximum supply (~1 billion for Minima), **NOT** your wallet balance.
> - Display `sendable` as the **primary balance** (what the user can spend).
> - Display `confirmed` as the full wallet balance.
> - Display `unconfirmed` as pending incoming.
> - **NEVER** display `total` as a balance.

---

## status

Returns general node info: version, chain height, memory, connected peers.

```json
{ "status": true, "response": {
  "version": "1.0.36",
  "devices": "1",
  "length": "1931455",
  "weight": "...",
  "minima": "1000000000",
  "coins": "12345",
  "data": "./minima/data",
  "memory": {
    "ram": "128MB",
    "disk": "2.1GB",
    "files": {
      "txpowdb": "500MB",
      "archivedb": "1.2GB",
      "cascade": "50MB",
      "chaintree": "100MB",
      "wallet": "1MB",
      "userdb": "500KB",
      "p2pdb": "200KB"
    }
  },
  "chain": {
    "block": "1931455",
    "time": "1706900000000",
    "hash": "0xABC...",
    "speed": "50",
    "difficulty": "0x068DB...",
    "size": "500",
    "length": "1931455",
    "weight": "...",
    "cascade": { ... }
  },
  "txpow": {
    "mempool": "0",
    "ramdb": "500",
    "txpowdb": "10000",
    "archivedb": "1500000"
  }
}}
```

| Field | Type | Meaning |
|-------|------|---------|
| `version` | string | Minima version |
| `devices` | string | Connected devices (parse with `int()`) |
| `length` | string | Chain height (parse with `int()`) |
| `minima` | string | Total Minima in circulation |
| `chain.block` | string | Current block number |
| `chain.time` | string | Block timestamp (millis since epoch) |
| `txpow.mempool` | string | Pending transactions in mempool |

> **AGENT WARNING:** `length`, `devices`, `coins`, `chain.block`, and virtually all numbers are **strings**. Parse with `int()`.

---

## send

Send Minima or tokens to an address. Returns full TxPoW on success.

**Parameters:** `address:MxG... amount:1 (tokenid:0x00) (split:N) (burn:N)`

### Success response:
```json
{ "status": true, "response": {
  "txpowid": "0xE121FF1C82B2B1E50A...",
  "isblock": false,
  "istransaction": false,
  "size": 5302,
  "burn": 0,
  "header": {
    "block": "1931455",
    "timemilli": "1770223384435",
    "date": "Wed Feb 04 16:43:04 GMT 2026"
  },
  "body": {
    "txn": {
      "inputs": [{ "coinid": "0x...", "amount": "2", "address": "0x...", "miniaddress": "MxG08...", "tokenid": "0x00" }],
      "outputs": [
        { "coinid": "0x...", "amount": "1", "address": "0x...", "miniaddress": "MxG08...", "tokenid": "0x00" },
        { "coinid": "0x...", "amount": "1", "address": "0x...", "miniaddress": "MxG08...", "tokenid": "0x00" }
      ],
      "transactionid": "0x8446..."
    }
  }
}}
```

### Error response:
```json
{ "status": false, "error": "Insufficient funds" }
```

| Field | Type | Meaning |
|-------|------|---------|
| `txpowid` | string | Transaction ID for explorer: `https://explorer.minima.global/transactions/<txpowid>` |
| `header.block` | string | Block height at transaction time |
| `header.timemilli` | string | Unix timestamp in milliseconds |
| `body.txn.inputs` | array | Coins consumed by this transaction |
| `body.txn.outputs` | array | Coins created (destination + change) |
| `body.txn.transactionid` | string | Internal tx hash (different from `txpowid`) |

> **AGENT WARNING:**
> - `txpowid` is the external transaction ID. Use it for explorer links.
> - `transactionid` is the internal hash — do **not** use for explorer links.
> - `amount` fields in inputs/outputs are **strings**.
> - `split:N` parameter (1-10) divides the amount into multiple output coins.
> - Use `getaddress` first to get own address for self-splits.

---

## hash

Hash data using Minima's Keccak-256 hash function.

**Parameters:** `data:hello` or `data:0xABCD`

```json
{ "status": true, "response": {
  "input": "hello",
  "hash": "0x1C8AFF950685C2ED4BC3174F3472287B56D9517B9C948127319A09A7A36DEAC8"
}}
```

| Field | Type | Meaning |
|-------|------|---------|
| `input` | string | Original input |
| `hash` | string | Keccak-256 result, `0x`-prefixed |

---

## random

Generate cryptographic random data using Minima's internal RNG.

```json
{ "status": true, "response": {
  "random": "0x6B585B893F66A452D09F9DDF50326BD938F4DEB1B1A0F4DC421959D42A857624"
}}
```

| Field | Type | Meaning |
|-------|------|---------|
| `random` | string | 256-bit random value, `0x`-prefixed |

---

## tokens

List all tokens known to this node.

```json
{ "status": true, "response": [{
  "tokenid": "0x00",
  "token": "Minima",
  "total": "1000000000",
  "decimals": "44",
  "script": "RETURN TRUE",
  "coinid": "0x00",
  "totalamount": "1000000000000000000000000000000000000000000000",
  "scale": "1"
}]}
```

| Field | Type | Meaning |
|-------|------|---------|
| `tokenid` | string | Token ID. `0x00` = native Minima |
| `token` | string or object | Name (string for Minima, object with `name`/`url`/`description` for custom tokens) |
| `total` | string | Token total supply (**NOT wallet balance**) |
| `decimals` | string | Decimal places (parse with `int()`) |
| `scale` | string | Scale factor (parse with `int()`) |

> **AGENT WARNING:** `total` here is the same concept as `balance.total` — it's the token supply, not how much you have. The `token` field can be a string **or** an object for custom tokens — always check the type.

---

## getaddress

Get the node's current default receiving address.

```json
{ "status": true, "response": {
  "script": "RETURN SIGNEDBY(0x18A7AFE7...)",
  "address": "0x2DF229042AA052477B3FC2388...",
  "miniaddress": "MxG081DU8KG8AY0A93NMFU272...",
  "simple": true,
  "default": true,
  "publickey": "0x18A7AFE76119922C493C41FF6F30F7B22E47594B0FB7DCE5C8BCE253E162CAC8",
  "track": true
}}
```

| Field | Type | Meaning |
|-------|------|---------|
| `address` | string | Hex address (`0x`-prefixed) |
| `miniaddress` | string | Human-readable `MxG`-prefixed address |
| `publickey` | string | Associated public key |

---

## maxima action:info

Get your Maxima identity and contact details.

```json
{ "status": true, "response": {
  "name": "noname",
  "publickey": "0x3081...",
  "mls": "Mx...@1.2.3.4:9001",
  "localidentity": "Mx...@192.168.1.1:9001",
  "p2pidentity": "Mx...@1.2.3.4:9001",
  "contact": "MxG18H...",
  "logs": false
}}
```

| Field | Type | Meaning |
|-------|------|---------|
| `name` | string | Display name (set with `maxima action:setname`) |
| `publickey` | string | Your Maxima public key |
| `mls` | string | Static MLS address (if configured) |
| `localidentity` | string | Local network identity |
| `p2pidentity` | string | Public network identity |
| `contact` | string | Full contact address for sharing |

> **AGENT WARNING:** `localidentity` vs `p2pidentity` — use `p2pidentity` for external/public contacts. `localidentity` is only reachable on the local network.

---

## maxcontacts action:list

List all Maxima contacts.

```json
{ "status": true, "response": [{
  "id": 0,
  "publickey": "0x3081...",
  "currentaddress": "Mx...@1.2.3.4:9001",
  "myaddress": "Mx...@1.2.3.4:9001",
  "lastseen": "1706900000000",
  "date": "Wed Feb 04 16:43:04 GMT 2026",
  "extradata": {
    "name": "Alice",
    "minimaaddress": "MxG08...",
    "topblock": "1931455",
    "checkblock": "1931400",
    "checkhash": "0xABC..."
  },
  "samechain": true
}]}
```

| Field | Type | Meaning |
|-------|------|---------|
| `id` | integer | Contact ID (use for send-by-ID) |
| `publickey` | string | Contact's Maxima public key |
| `currentaddress` | string | Contact's current reachable address |
| `lastseen` | string | Unix timestamp in millis (STRING) |
| `extradata.name` | string | Contact's display name |
| `samechain` | boolean | Whether contact is on same chain |

---

## backup

Create a backup of the node.

**Parameters:** `(password:YourPassword)`

```json
{ "status": true, "response": {
  "backup": {
    "file": "/path/to/minima-backup-2026-02-04.bak",
    "size": "2.1MB"
  }
}}
```

> **AGENT WARNING:** Backups contain private keys. Always encrypt with a password. Never transmit unencrypted backups.

---

## vault

Manage private keys and seed phrase.

**Parameters:** `(action:seed|wipekeys|restorekeys|passwordlock|passwordunlock) (seed:...) (phrase:...) (password:...) (confirm:...)`

### Default (no action) — show seed phrase:
```json
{ "status": true, "response": {
  "phrase": "word1 word2 word3 ... word24",
  "modifier": "0x00",
  "locked": false,
  "depth": { ... }
}}
```

| Field | Type | Meaning |
|-------|------|---------|
| `phrase` | string | 24-word seed phrase |
| `locked` | boolean | Whether keys are password-locked |

> **AGENT WARNING:** This command exposes the seed phrase. **Never log, display, or transmit it.** This is the master key — if lost, funds are unrecoverable. Always require user confirmation before executing `vault`.
