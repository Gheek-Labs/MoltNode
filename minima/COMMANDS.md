# Minima RPC Command Reference

Complete command list for agent programmatic access via `http://localhost:9005/<command>`.

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
| `balance` | Show balances |
| `coins` | List coins |
| `keys` | List wallet keys |
| `getaddress` | Get default address |
| `newaddress` | Create new address |
| `tokens` | List tokens |
| `tokencreate` | Create a token |

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
| `tutorial` | KISSVM tutorial |

## Maxima Messaging
| Command | Description |
|---------|-------------|
| `maxima action:info` | Maxima info |
| `maxima action:send to:Mx.. data:hello` | Send message |
| `maxcontacts action:list` | List contacts |
| `maxcontacts action:add contact:Mx..` | Add contact |

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
| `vault action:seed` | View seed phrase |
| `archive` | Archive sync |

## MiniDApps
| Command | Description |
|---------|-------------|
| `mds action:list` | List MiniDApps |
| `mds action:install file:app.mds.zip` | Install MiniDApp |
| `mds action:uninstall uid:...` | Uninstall MiniDApp |

## System
| Command | Description |
|---------|-------------|
| `help` | Full help |
| `rpc` | RPC settings |
| `webhooks` | Manage webhooks |
| `quit` | Shutdown node |

## Example Agent Usage

```python
import requests

def rpc(cmd):
    return requests.get(f"http://localhost:9005/{cmd}").json()

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
# Via curl
curl "http://localhost:9005/status"
curl "http://localhost:9005/balance"
curl "http://localhost:9005/send%20address:MxG...%20amount:1"
```
