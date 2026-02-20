# Minima Node - One-Click Bootstrap

## Overview
A one-click, agent-friendly, headless Minima blockchain node setup with stable MxID identity system and natural language chat interface. The node runs with RPC enabled for programmatic interaction.

## Project Structure
```
/
├── bootstrap.sh       # One-click setup script
├── chat/              # Natural language chat interface
│   ├── app.py         # Flask web server (port 5000)
│   ├── minima_agent.py # LLM agent + command execution
│   ├── providers/     # LLM provider abstraction
│   │   ├── base.py    # Abstract base class
│   │   ├── openai_provider.py    # OpenAI/Replit AI
│   │   ├── anthropic_provider.py # Claude
│   │   ├── ollama_provider.py    # Local models
│   │   └── custom_provider.py    # OpenAI-compatible
│   ├── templates/     # HTML templates
│   └── static/        # CSS styles
├── integration/           # Language integration kits
│   ├── python/
│   │   └── minima_client.py   # Python RPC client (normalized responses)
│   └── node/
│       └── minima-client.js   # Node.js RPC client (ESM, JSDoc typed)
├── minima/
│   ├── minima.jar     # Minima node JAR (downloaded on first run)
│   ├── start.sh       # Node startup script
│   ├── cli.sh         # Agent-friendly CLI wrapper
│   ├── get_maxima.sh  # Get current Maxima address
│   ├── mds_install.sh         # Install MiniDapps (URL/file)
│   ├── mds_list.sh            # List installed MiniDapps
│   ├── mds_api.sh             # Call MiniDapp API endpoints
│   ├── mds_store.sh           # Manage MiniDapp stores
│   ├── MINIDAPPS.md           # MiniDapp guide and store directory
│   ├── mxid_init.sh         # Full MxID wizard (with auto-detection)
│   ├── mxid_setup_mls.sh    # Set Static MLS
│   ├── mxid_register_permanent.sh  # Register Permanent MAX#
│   ├── mxid_lockdown_contacts.sh   # Contact anti-spam
│   ├── mxid_claim.sh        # Claim MxID identity
│   ├── mxid_info.sh         # Identity card JSON
│   ├── mxid_challenge.sh    # Generate verification challenge (Minima RNG)
│   ├── mxid_sign.sh         # Sign with Maxima key
│   ├── mxid_verify.sh       # Verify signature
│   ├── MXID.md              # MxID specification
│   ├── KISSVM.md                # KISSVM scripting language glossary
│   ├── ONCHAIN_RECORDS.md      # On-chain data record guide (txn builder recipe)
│   ├── record_data.sh         # Post data on-chain (--data/--port/--burn/--mine)
│   ├── WEBHOOKS.md              # Webhook event catalog + payloads
│   ├── BACKUP.md              # Backup, restore, resync guide
│   ├── AGENT_QUICKSTART.md    # Agent operations guide
│   ├── COMMANDS.md            # Full RPC command reference
│   ├── RESPONSE_SCHEMAS.md    # Human/agent-readable response schemas
│   ├── rpc/schemas/           # Machine-readable JSON schemas
│   │   ├── balance.schema.json
│   │   ├── status.schema.json
│   │   ├── hash.schema.json
│   │   ├── txnpost.schema.json
│   │   ├── tokens.schema.json
│   │   └── send.schema.json
│   └── data/                  # Node data directory (gitignored)
├── templates/             # Reference implementations
│   ├── node-web-dashboard/    # Express dashboard (3-balance display)
│   ├── node-webhook-listener/ # Webhook event listener (zero-dep Node.js)
│   ├── python-bot/            # CLI balance/status monitor
│   └── ros2-bridge/           # ROS2 topic bridge skeleton
└── README.md          # Documentation
```

## MxID - Stable Agent Identity
MxID provides a reachable, stable identity that survives restarts/IP changes.

**Prerequisites:** `jq` installed

**Quick setup:** `./minima/mxid_init.sh`

**Manual order:** mxid_setup_mls.sh → mxid_register_permanent.sh → mxid_lockdown_contacts.sh → mxid_claim.sh

**Primitives:** mxid_info.sh, mxid_challenge.sh, mxid_sign.sh, mxid_verify.sh

### MLS Auto-Detection
The wizard auto-detects if your node can be its own MLS (public IPv4 + port listening):
- **Sovereign**: Public IP + listening port → self-MLS
- **Community**: Private IP + COMMUNITY_MLS_HOST set → shared MLS (prints graduation command)
- **Manual**: Otherwise → user input

Env vars: `AUTO_DETECT_MLS`, `PREFER_SOVEREIGN_MLS`, `COMMUNITY_MLS_HOST`, `P2P_PORT`

### Graduation Command
When community MLS is selected, the wizard prints a single command to upgrade to sovereignty later:
```bash
./minima/cli.sh maxextra action:staticmls host:$(./minima/cli.sh maxima | jq -r '.response.p2pidentity')
```

## Quick Start
1. Run `./bootstrap.sh` to initialize
2. Node starts via workflow automatically
3. Interact via `./minima/cli.sh <command>` or HTTP API

## RPC Interface
- **Port**: 9005
- **URL**: `http://localhost:9005/<command>`

### Common Commands
- `status` - Node status and sync info
- `balance` - Wallet balance
- `help` - All available commands
- `peers` - Connected peers
- `network` - Network info

## Configuration
| Setting | Value |
|---------|-------|
| RPC Port | 9005 |
| P2P Port | 9001 |
| MDS Port | 9003 (SSL, password-protected) |
| Data Dir | ./minima/data |
| Bootstrap Node | megammr.minima.global:9001 |

## MDS (MiniDapp System)
- **Port**: 9003 (SSL-encrypted, password-authenticated)
- **Security**: High-entropy password required (16+ chars, mixed case, numbers, symbols)
- **Access**: `https://localhost:9003` (or `https://<server-ip>:9003` if exposed)
- **Password**: Set via `MDS_PASSWORD` secret, or auto-generated on startup
- **Note**: Block port 9003 at firewall if external access not needed

## Natural Language Chat Interface
- **Port**: 5000
- **URL**: Open the webview to access the chat UI

### Features
- Ask questions in natural language: "What's my balance?", "Show node status"
- Automatic command execution for safe queries
- Confirmation required for transactions (send), vault, and backup
- Pluggable LLM providers (OpenAI, Anthropic, Ollama, custom)

### Configuration
Set LLM provider via environment variables:
| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_PROVIDER` | openai, anthropic, ollama, custom | openai |
| `LLM_MODEL` | Model name (e.g., gpt-4o-mini) | provider default |
| `LLM_BASE_URL` | Custom API endpoint (for custom provider) | - |
| `LLM_API_KEY` | API key for custom provider | - |

Replit AI Integration is used by default (no API key needed).

## RPC Quirks + Balance Semantics

**Critical for any agent reading Minima RPC responses:**

### Balance fields
| Field | Meaning | Use for |
|-------|---------|---------|
| `sendable` | What you can spend right now | **Primary balance display** |
| `confirmed` | Full wallet balance (includes locked) | Full balance |
| `unconfirmed` | Pending incoming | Pending indicator |
| `total` | Token max supply / hardcap (~1B for Minima) | **NEVER display as balance** |

### Response format
- All RPC responses are JSON: `{"status": true/false, "response": ...}`
- **Mixed types:** Some numeric fields are integers (e.g., `length`, `chain.block`, `txpow.*`), others are strings (e.g., `weight`, `minima`, `coins`, `confirmed`). Use `_safe_int()`/`safeInt()` which handles both.
- The `devices` field does **NOT** exist in the status response
- `chain.time` is a date string, NOT millis. `chain.speed` is a float.
- `tokens` response uses `name` field; `balance` response uses `token` field (different names!)
- `balance tokendetails:true` returns rich metadata including `details.decimals` (integer; 0 = NFT)
- HTTP responses use LF-only line endings — use a JSON parser, never regex
- Hex values are prefixed with `0x`

### Response schemas
See `minima/RESPONSE_SCHEMAS.md` for complete field semantics, types, and agent warnings.
Machine-readable schemas in `minima/rpc/schemas/*.schema.json`.

## Recent Changes
- 2026-02-20: Phase 3+4: KISSVM glossary (KISSVM.md), transaction builder recipe in ONCHAIN_RECORDS.md, rewritten record_data.sh with --data/--port/--burn/--mine flags, SDK port/burn support. Webhooks: live-captured 4 event types (NEWBLOCK, MINING, MDS_TIMER_10S/60S), created WEBHOOKS.md with full payload docs, node-webhook-listener template.
- 2026-02-20: Phase 6: Full schema coverage — 25 RPC command schemas. Updated send schema with live transaction response (superblock/cascadelevels int, nonce/magic strings, witness/burntxn/txnlist structure). Added schemas: keys, newaddress, scripts, history, mds, burn, tokencreate, consolidate, maxsign, maxverify. Updated RESPONSE_SCHEMAS.md with all 25 command sections. Updated maxcontacts to show allowallcontacts wrapper.
- 2026-02-20: Phase 5: Live-validated schemas, SDKs, and templates against running node. Fixed: status (removed devices, corrected int/float types), hash (added data/type fields), random (added size/hashed/type/keycode), tokens (decimals/scale are int, name vs token field), maxima (added icon/mxpublickey/staticmls/poll). Added balance tokendetails:true + NFT detection (decimals:0). Added nfts() to both SDKs.
- 2026-02-20: Phase 4: On-chain record recipe (ONCHAIN_RECORDS.md, record_data.sh, SDK recordOnChain helpers, hash schema warnings)
- 2026-02-20: Added templates: node-web-dashboard, python-bot, ros2-bridge
- 2026-02-20: Added language integration kits (integration/python + integration/node)
- 2026-02-20: Added response schema system (RESPONSE_SCHEMAS.md + rpc/schemas/*.schema.json)
- 2026-02-20: Phase 0 doc hotfixes: balance warnings in COMMANDS.md, AGENT_QUICKSTART.md, replit.md
- 2026-02-04: Added natural language chat interface with pluggable LLM providers
- 2026-02-04: Renamed MoltID to MxID everywhere (scripts and docs)
- 2026-02-03: JAR now downloaded from GitHub on first run (removed 72MB from repo)
- 2026-02-03: Added FEATURES.md - complete feature list documentation
- 2026-02-03: Added "Explore MDS" as step 4 in quickstart guides
- 2026-02-03: Enabled MDS with high-entropy password validation and auto-generation
- 2026-02-03: Restructured AGENT_QUICKSTART.md (backup → MxID → operations)
- 2026-02-02: Added MLS auto-detection to mxid_init.sh wizard
- 2026-02-02: Added complete MxID Phase-0 primitives (9 scripts)
- 2026-02-02: Added Moltbook verification ritual documentation
- 2026-02-02: Initial setup - one-click headless Minima node with RPC
