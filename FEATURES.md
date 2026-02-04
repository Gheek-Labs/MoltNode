# MxNode - Full Feature List

## Core Minima Node Features

### One-Click Setup
- `bootstrap.sh` - Single command to initialize entire node
- Auto-downloads Minima JAR if missing
- Creates all necessary directories and scripts
- Configures RPC, P2P, and MDS ports automatically

### Headless Operation
- Runs without GUI or user interaction
- Agent-friendly CLI wrapper (`cli.sh`)
- All commands return JSON for programmatic parsing
- Designed for autonomous agent control

### Network Connectivity
- **RPC Port 9005** - HTTP API for all node commands
- **P2P Port 9001** - Peer-to-peer blockchain network
- **MDS Port 9003** - SSL-encrypted MiniDapp system
- Auto-connects to Minima bootstrap nodes

---

## MxID - Stable Identity System

### Identity Components
- **Permanent MAX# Address** - Survives IP changes and restarts
- **Static MLS** - Message Layer Service for reliable reachability
- **Contact Lockdown** - Anti-spam protection for contacts list
- **Moltbook Verification** - Public identity verification ritual

### Identity Scripts
| Script | Purpose |
|--------|---------|
| `mxid_init.sh` | Full identity wizard with auto-detection |
| `mxid_setup_mls.sh` | Configure Static MLS |
| `mxid_register_permanent.sh` | Register Permanent MAX# |
| `mxid_lockdown_contacts.sh` | Enable contact anti-spam |
| `mxid_claim.sh` | Claim MxID identity |
| `mxid_info.sh` | Output identity card as JSON |

### Cryptographic Primitives
| Script | Purpose |
|--------|---------|
| `mxid_challenge.sh` | Generate verification challenge (Minima RNG) |
| `mxid_sign.sh` | Sign data with Maxima private key |
| `mxid_verify.sh` | Verify signature against public key |

### MLS Auto-Detection
- Detects public IPv4 and listening port
- **Sovereign Mode** - Self-MLS when publicly reachable
- **Community Mode** - Shared MLS with graduation command
- **Manual Mode** - User-provided MLS configuration
- Environment variables: `AUTO_DETECT_MLS`, `PREFER_SOVEREIGN_MLS`, `COMMUNITY_MLS_HOST`

---

## MDS - MiniDapp System

### Core Features
- **SSL Encryption** - All traffic encrypted
- **Password Authentication** - High-entropy password required
- **Trust Levels** - Read/write permission control
- **30+ Pre-installed MiniDapps** - Ready to use

### MDS Management Scripts
| Script | Purpose |
|--------|---------|
| `mds_list.sh` | List installed MiniDapps (JSON/table/UID output) |
| `mds_install.sh` | Install from URL or local file |
| `mds_api.sh` | Call MiniDapp API endpoints |
| `mds_store.sh` | Manage community MiniDapp stores |

### Community Stores (8 Built-in)
| Shortname | Developer |
|-----------|-----------|
| `spartacusrex` | Minima founder |
| `panda` | Panda developer |
| `kisslabs` | KissLabs team |
| `dynamitesush` | Dynamite Sush |
| `jazminima` | Jazminima |
| `monthrie` | Monthrie |
| `ipfs` | IPFS gateway |
| `mininft` | MiniNFT team |

### Notable MiniDapps
- **Soko** - NFT marketplace with agent API
- **Miniswap** - Decentralized exchange
- **Token Studio** - Create custom tokens
- **Wallet** - Balance and transaction management
- **MaxSolo** - Solo messaging
- **Pending** - Transaction approval queue

---

## Backup & Recovery

### Backup Methods
- **Seed Phrase** - 24-word recovery phrase via `vault` command
- **Archive Backup** - Full node state export
- **Key Export** - Individual key backup

### Recovery Options
- **Seed Restore** - Rebuild from 24-word phrase
- **Archive Restore** - Full state recovery
- **Resync** - Fresh sync from network
- **Megammr Resync** - Fast sync from archive node

### Documentation
- `BACKUP.md` - Complete backup and restore guide

---

## Maxima Messaging

### Contact Management
- Add/remove contacts by address
- Search contacts by public key
- Contact limit recommendations (~20 for optimal performance)
- Tx-PoW maintenance for each contact

### Message Operations
- Send by address, ID, or public key
- Polling mode for reliable delivery
- Broadcast to all contacts
- Custom application identifiers

### Cryptography
- Sign messages with Maxima ID
- Verify signatures with public keys
- Create custom RSA keypairs

---

## RPC API

### Access Methods
- HTTP GET: `http://localhost:9005/<command>`
- CLI wrapper: `./minima/cli.sh <command>`
- URL-encoded parameters supported

### Key Commands
| Command | Purpose |
|---------|---------|
| `status` | Node status and sync info |
| `balance` | Wallet balances |
| `send` | Transfer value |
| `maxima` | Messaging operations |
| `maxcontacts` | Contact management |
| `mds` | MiniDapp management |
| `vault` | Seed phrase access |
| `help` | Full command list |

---

## Security Features

### MDS Security
- High-entropy password (16+ chars, mixed case, numbers, symbols)
- Auto-generation if not provided
- SSL/TLS encryption on port 9003
- Localhost binding by default

### Identity Security
- Contact lockdown prevents unsolicited additions
- Signature verification for all messages
- Challenge-response authentication
- Private key never exposed

### Network Security
- RPC on localhost only
- Configurable firewall recommendations
- No external access by default

---

## Agent Integration

### Design Principles
- All output is JSON parseable
- Scripts return exit codes for error handling
- Environment variable configuration
- Stateless command execution

### Python Example Included
- Full working agent code in AGENT_QUICKSTART.md
- HTTP and subprocess patterns
- Error handling examples

### Documentation
| File | Contents |
|------|----------|
| `AGENT_QUICKSTART.md` | Step-by-step agent guide |
| `COMMANDS.md` | Full RPC command reference |
| `MXID.md` | Identity system specification |
| `MINIDAPPS.md` | MiniDapp guide with API examples |
| `BACKUP.md` | Backup and recovery procedures |

---

## Configuration

| Setting | Default Value |
|---------|---------------|
| RPC Port | 9005 |
| P2P Port | 9001 |
| MDS Port | 9003 |
| Data Directory | `./minima/data` |
| Bootstrap Node | `megammr.minima.global:9001` |
| MDS Password | `MDS_PASSWORD` env var or auto-generated |

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `MDS_PASSWORD` | MDS authentication password |
| `SESSION_SECRET` | Session encryption key |
| `AUTO_DETECT_MLS` | Enable MLS auto-detection |
| `PREFER_SOVEREIGN_MLS` | Prefer self-MLS when possible |
| `COMMUNITY_MLS_HOST` | Fallback community MLS server |
| `P2P_PORT` | Override default P2P port |
