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
│   ├── COMMANDS.md    # Full RPC command reference
│   └── data/          # Node data directory (gitignored)
└── README.md          # Documentation
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
| Data Dir | ./minima/data |
| Bootstrap Node | megammr.minima.global:9001 |

## Recent Changes
- 2026-02-02: Initial setup - one-click headless Minima node with RPC
