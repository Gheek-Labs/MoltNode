# Minima Node - One-Click Bootstrap

Agent-friendly, headless Minima blockchain node setup.

## Quick Start

```bash
./bootstrap.sh
./minima/start.sh
```

## Documentation

| Document | Description |
|----------|-------------|
| [Agent Quickstart](minima/AGENT_QUICKSTART.md) | Essential operations for agents |
| [Commands Reference](minima/COMMANDS.md) | Full RPC command list |

## Agent Quickstart

**1. Run node:** `./minima/start.sh`

**2. Get Maxima address:** `./minima/get_maxima.sh`

**3. Send value:** `./minima/cli.sh send address:MxG... amount:1`

**4. Add contact:** `./minima/cli.sh maxcontacts action:add contact:MxG...@IP:PORT`

**5. Send message:** `./minima/cli.sh maxima action:send to:MxG... application:app data:hello`

See [AGENT_QUICKSTART.md](minima/AGENT_QUICKSTART.md) for full details.

## RPC Interface

Once running, interact via CLI or HTTP:

### CLI Commands
```bash
./minima/cli.sh status     # Node status
./minima/cli.sh balance    # Wallet balance
./minima/get_maxima.sh     # Current Maxima address
```

### HTTP API
```bash
curl http://localhost:9005/status
curl http://localhost:9005/balance
curl "http://localhost:9005/maxima%20action:info"
```

## Configuration

| Setting | Value |
|---------|-------|
| RPC Port | 9005 |
| P2P Port | 9001 |
| Data Dir | ./minima/data |

## Ports

- **9001**: P2P network connections
- **9005**: RPC interface (agent commands)
