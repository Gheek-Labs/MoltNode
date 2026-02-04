# Minima Node - One-Click Bootstrap

## Overview
A one-click, agent-friendly, headless Minima blockchain node setup with stable MxID identity system. The node runs with RPC enabled for programmatic interaction.

## Project Structure
```
/
├── bootstrap.sh       # One-click setup script
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
│   ├── BACKUP.md              # Backup, restore, resync guide
│   ├── AGENT_QUICKSTART.md    # Agent operations guide
│   ├── COMMANDS.md            # Full RPC command reference
│   └── data/                  # Node data directory (gitignored)
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

## Recent Changes
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
