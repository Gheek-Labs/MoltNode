# Minima RPC Command Reference

Complete command list for agent programmatic access via `http://localhost:9005/<command>`.

**Related guides:** [Agent Quickstart](AGENT_QUICKSTART.md) | [Backup & Restore](BACKUP.md) | [MxID](MXID.md)

## Syntax
- `[]` = required parameter
- `()` = optional parameter
- Chain commands with `;`

## Node Info
| Command | Description |
|---------|-------------|
| `status` | Show general status |
| `block` | Current top block |
| `network` | Network status |
| `burn` | View burn metrics |
| `printtree` | Print blockchain tree |
| `scanchain` | Scan chain history |

## Wallet
| Command | Description |
|---------|-------------|
| `balance` | Show balances (see schema below) |
| `coins` | List coins |
| `keys` | List wallet keys |
| `getaddress` | Get default address |
| `newaddress` | Create new address |
| `tokens` | List tokens |
| `tokencreate` | Create a token |

### `balance` response schema

```json
{ "status": true, "response": [{
  "token": "Minima",
  "tokenid": "0x00",
  "confirmed": "1000",      // Full wallet balance (includes locked)
  "unconfirmed": "0",       // Received but pending confirmations
  "sendable": "1000",       // Available to spend (confirmed minus locked)
  "coins": "3",             // Number of UTXO coins
  "total": "1000000000"     // TOKEN MAX SUPPLY — NOT your balance
}]}
```

> **AGENT WARNING — `total` is a trap:**
> `total` is the token's maximum supply / hardcap, **NOT** "your wallet balance".
> - Display `sendable` as the primary balance (what the user can spend).
> - Display `confirmed` as the full wallet balance (includes locked coins).
> - Display `unconfirmed` as pending incoming.
> - **Never** display `total` as a balance — it is ~1 billion for Minima.

See also: [RESPONSE_SCHEMAS.md](RESPONSE_SCHEMAS.md) for full field semantics.

## Transactions
| Command | Description |
|---------|-------------|
| `send address:0x.. amount:1` | Send Minima |
| `history` | Transaction history |
| `txpow` | Search for TxPoW |
| `consolidate tokenid:0x00` | Consolidate coins |

## Transaction Builder
| Command | Description |
|---------|-------------|
| `txncreate id:mytx` | Create transaction |
| `txninput id:mytx coinid:0x..` | Add input |
| `txnoutput id:mytx amount:1 address:0x..` | Add output |
| `txnsign id:mytx publickey:auto` | Sign transaction |
| `txnpost id:mytx` | Post transaction |
| `txnlist` | List transactions |
| `txndelete id:mytx` | Delete transaction |

## Scripts
| Command | Description |
|---------|-------------|
| `scripts` | List scripts |
| `newscript script:"RETURN TRUE"` | Add script |
| `runscript script:"..."` | Run script |
| `tutorial` | KISSVM scripts tutorial |

## Maxima P2P Messaging

### maxima - Core Messaging

| Command | Description |
|---------|-------------|
| `maxima action:info` | Your Maxima details (name, publickey, contact address) |
| `maxima action:setname name:MyName` | Set display name for contacts |
| `maxima action:hosts` | List your Maxima hosts |
| `maxima action:send id:1 application:app data:0x..` | Send to contact by ID |
| `maxima action:send to:MxG.. application:app data:0x..` | Send to contact address |
| `maxima action:send publickey:0x.. application:app data:0x.. poll:true` | Send with retry |
| `maxima action:sendall application:app data:0x..` | Broadcast to ALL contacts |
| `maxima action:refresh` | Refresh/re-sync contacts |

### maxcontacts - Contact Management

> **Agent Note:** Each contact consumes Tx-PoW. Limit to ~20 contacts. Use `poll:true` when sending for automatic retry on offline contacts.

| Command | Description |
|---------|-------------|
| `maxcontacts action:list` | List all contacts |
| `maxcontacts action:add contact:MxG..@IP:PORT` | Add contact |
| `maxcontacts action:remove id:1` | Remove contact by ID |
| `maxcontacts action:search publickey:0x..` | Search by publickey |
| `maxcontacts action:search id:1` | Search by ID |

### maxextra - Advanced/Permanent Addresses

| Command | Description |
|---------|-------------|
| `maxextra action:staticmls host:Mx..@IP:PORT` | Set static MLS host |
| `maxextra action:staticmls host:clear` | Clear static MLS |
| `maxextra action:addpermanent publickey:0x..` | Register for public lookup |
| `maxextra action:removepermanent publickey:0x..` | Remove from public lookup |
| `maxextra action:listpermanent` | List registered publickeys |
| `maxextra action:getaddress maxaddress:MAX#0x..#Mx..@IP:PORT` | Get contact address from MLS |
| `maxextra action:mlsinfo` | MLS usage info |
| `maxextra action:allowallcontacts enable:true\|false` | Control new contacts |
| `maxextra action:addallowed publickey:0x..` | Allow specific contact |
| `maxextra action:listallowed` | List allowed publickeys |
| `maxextra action:clearallowed` | Clear allowed list |

### maxsign / maxverify - Cryptographic Signatures

| Command | Description |
|---------|-------------|
| `maxcreate` | Create 128-bit RSA keypair |
| `maxsign data:0x..` | Sign with Maxima ID |
| `maxsign data:0x.. privatekey:0x..` | Sign with custom key |
| `maxverify data:0x.. publickey:0x.. signature:0x..` | Verify signature |

## Cryptography
| Command | Description |
|---------|-------------|
| `hash data:hello` | Hash data |
| `random` | Generate random |
| `sign publickey:0x.. data:hello` | Sign data |
| `verify publickey:0x.. data:hello signature:0x..` | Verify signature |

## Backup/Restore
| Command | Description |
|---------|-------------|
| `backup` | Create backup |
| `restore file:backup.bak` | Restore backup |
| `vault` | `action:seed\|wipekeys\|restorekeys\|passwordlock\|passwordunlock` `seed:` `phrase:` - **BE CAREFUL.** Wipe/Restore/Encrypt/Decrypt your private keys |
| `archive` | Archive sync |

## MiniDApps (MDS)

MDS (MiniDapp System) runs on port **9003** (P2P port + 2) with SSL.

**Security:** MDS requires password authentication. Access via `https://localhost:9003`

| Command | Description |
|---------|-------------|
| `mds` | Show MDS status and password |
| `mds action:list` | List MiniDApps |
| `mds action:install file:app.mds.zip` | Install MiniDApp |
| `mds action:uninstall uid:...` | Uninstall MiniDApp |

## System
| Command | Description |
|---------|-------------|
| `help` | Full help. Use `help command:<cmd>` for detailed info on a specific command (e.g., `help command:status`) |
| `rpc` | RPC settings |
| `webhooks` | `action:list\|add\|remove\|clear` `hook:<url>` - Add a webhook that is called with Minima events as they happen |
| `quit` | Shutdown node |

## Quick Access Scripts

| Script | Purpose |
|--------|---------|
| `./get_maxima.sh` | Get current Maxima address (rotates frequently) |
| `./cli.sh <cmd>` | Run any RPC command with formatted output |

## Example Agent Usage

```python
import requests
import subprocess

def rpc(cmd):
    return requests.get(f"http://localhost:9005/{cmd}").json()

# Get current Maxima address (recommended method)
maxima_addr = subprocess.check_output(["./minima/get_maxima.sh"]).decode().strip()

# Node status
rpc("status")

# Get balance
rpc("balance")

# Send transaction
rpc("send address:MxG... amount:1")

# Create token
rpc("tokencreate name:MyToken amount:1000000")
```

```bash
# Get current Maxima address
./minima/get_maxima.sh

# Via curl
curl "http://localhost:9005/status"
curl "http://localhost:9005/balance"
curl "http://localhost:9005/maxima%20action:info"
```
