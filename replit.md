# Minima Node - One-Click Bootstrap

## Overview
A one-click, agent-friendly, headless Minima blockchain node setup. The node runs with RPC enabled for programmatic interaction.

## Project Structure
```
/
├── bootstrap.sh       # One-click setup script
├── minima/
│   ├── minima.jar     # Minima node JAR
│   ├── start.sh       # Node startup script
│   ├── cli.sh         # Agent-friendly CLI wrapper
│   ├── get_maxima.sh  # Get current Maxima address
│   ├── moltid_init.sh         # Full MoltID wizard
│   ├── moltid_setup_mls.sh    # Set Static MLS
│   ├── moltid_register_permanent.sh  # Register Permanent MAX#
│   ├── moltid_lockdown_contacts.sh   # Contact anti-spam
│   ├── moltid_claim.sh        # Claim MoltID identity
│   ├── moltid_info.sh         # Identity card JSON
│   ├── moltid_challenge.sh    # Generate verification challenge
│   ├── moltid_sign.sh         # Sign with Maxima key
│   ├── moltid_verify.sh       # Verify signature
│   ├── MOLTID.md              # MoltID specification
│   ├── AGENT_QUICKSTART.md    # Agent operations guide
│   ├── COMMANDS.md            # Full RPC command reference
│   └── data/                  # Node data directory (gitignored)
└── README.md          # Documentation
```

## MoltID - Stable Agent Identity
MoltID provides a reachable, stable identity that survives restarts/IP changes.

**Quick setup:** `./minima/moltid_init.sh`

**Manual order:** moltid_setup_mls.sh → moltid_register_permanent.sh → moltid_lockdown_contacts.sh → moltid_claim.sh

**Primitives:** moltid_info.sh, moltid_challenge.sh, moltid_sign.sh, moltid_verify.sh

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
| Data Dir | ./minima/data |
| Bootstrap Node | megammr.minima.global:9001 |

## Recent Changes
- 2026-02-02: Added complete MoltID Phase-0 primitives (8 scripts)
- 2026-02-02: Added Moltbook verification ritual documentation
- 2026-02-02: Initial setup - one-click headless Minima node with RPC
