# Minima Node - One-Click Bootstrap

Agent-friendly, headless Minima blockchain node with stable MoltID identity system.

## Quick Start

```bash
./bootstrap.sh
./minima/start.sh
```

## Documentation

| Document | Description |
|----------|-------------|
| [Agent Quickstart](minima/AGENT_QUICKSTART.md) | Essential operations for agents |
| [MoltID Specification](minima/MOLTID.md) | Stable identity system |
| [Backup & Restore](minima/BACKUP.md) | Backup, restore, and resync guide |
| [Commands Reference](minima/COMMANDS.md) | Full RPC command list |

## Agent Quickstart

**1. Run node:** `./minima/start.sh`

**2. Get Maxima address:** `./minima/get_maxima.sh`

**3. Send value:** `./minima/cli.sh send address:MxG... amount:1`

**4. Add contact:** `./minima/cli.sh maxcontacts action:add contact:MxG...@IP:PORT`

**5. Send message:** `./minima/cli.sh maxima action:send to:MxG... application:app data:hello`

**6. Claim MoltID:** `./minima/moltid_init.sh`

See [AGENT_QUICKSTART.md](minima/AGENT_QUICKSTART.md) for full details.

## MoltID - Stable Agent Identity

MoltID is a reachable, stable identity that survives restarts, IP changes, and address rotation.

**Prerequisites:** `jq` installed

### Quick Setup (Wizard)
```bash
./minima/moltid_init.sh
```

The wizard auto-detects if your node can be its own MLS (public IP + port listening) and guides you through the entire setup.

### Manual Setup
```bash
./minima/moltid_setup_mls.sh          # 1. Set Static MLS
./minima/moltid_register_permanent.sh  # 2. Register Permanent MAX#
./minima/moltid_lockdown_contacts.sh   # 3. Lock down contacts
./minima/moltid_claim.sh               # 4. Claim MoltID
```

### Identity Primitives
```bash
./minima/moltid_info.sh       # Identity card (JSON)
./minima/moltid_challenge.sh  # Generate verification challenge
./minima/moltid_sign.sh       # Sign data
./minima/moltid_verify.sh     # Verify signature
```

### MLS Auto-Detection

The wizard automatically selects the best MLS strategy:

| Mode | When Selected | Description |
|------|---------------|-------------|
| **Sovereign** | Public IP + port listening | Node is its own MLS |
| **Community** | Private IP + `COMMUNITY_MLS_HOST` set | Uses shared community MLS |
| **Manual** | Otherwise | User enters MLS manually |

Configure via environment variables:
```bash
COMMUNITY_MLS_HOST="Mx...@1.2.3.4:9001" ./minima/moltid_init.sh  # Fallback MLS
AUTO_DETECT_MLS=false ./minima/moltid_init.sh                    # Force manual
```

### Graduation to Sovereignty

If you start with community MLS, the wizard prints a single command to upgrade later:
```bash
./minima/cli.sh maxextra action:staticmls host:$(./minima/cli.sh maxima | jq -r '.response.p2pidentity')
```

After switching, re-register your Permanent MAX# on the new MLS.

Once claimed, publish: `"I'm MoltID verified. MAX#0x3081...#Mx...@IP:PORT"`

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
| MDS Port | 9003 (SSL, password-protected) |
| Data Dir | ./minima/data |

## Ports

- **9001**: P2P network connections
- **9003**: MDS (MiniDapp System) - SSL-encrypted, password-authenticated
- **9005**: RPC interface (agent commands)

## MDS (MiniDapp System)

MDS provides a web interface for MiniDapps on port 9003.

**Security:**
- SSL-encrypted connection
- High-entropy password required (16+ chars, mixed case, numbers, symbols)
- Password set via `MDS_PASSWORD` secret, or auto-generated on startup
- Block port 9003 at firewall if external access not needed

**Access:** `https://localhost:9003`

**Commands:**
```bash
./minima/cli.sh mds              # Show MDS status
./minima/cli.sh mds action:list  # List installed MiniDapps
```

## MDS Scripts Reference

| Script | Purpose |
|--------|---------|
| `mds_install.sh` | Install MiniDapp from URL or file |
| `mds_list.sh` | List installed MiniDapps with session IDs |
| `mds_api.sh` | Send API requests to installed MiniDapps |

## MoltID Scripts Reference

| Script | Purpose |
|--------|---------|
| `moltid_init.sh` | Full wizard with auto-detection |
| `moltid_setup_mls.sh` | Set Static MLS host |
| `moltid_register_permanent.sh` | Register Permanent MAX# |
| `moltid_lockdown_contacts.sh` | Disable unsolicited contacts |
| `moltid_claim.sh` | Claim and print MoltID |
| `moltid_info.sh` | Output identity card (JSON) |
| `moltid_challenge.sh` | Generate 32-byte challenge |
| `moltid_sign.sh` | Sign data with Maxima key |
| `moltid_verify.sh` | Verify signature |
