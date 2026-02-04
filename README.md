# Minima Node - One-Click Bootstrap

Agent-friendly, headless Minima blockchain node with stable MxID identity system.

## Quick Start

```bash
./bootstrap.sh
./minima/start.sh
```

On first run, the Minima JAR (~70MB) is downloaded automatically from GitHub.

## Documentation

| Document | Description |
|----------|-------------|
| [Full Feature List](FEATURES.md) | Complete capabilities overview |
| [Agent Quickstart](minima/AGENT_QUICKSTART.md) | Essential operations for agents |
| [MiniDapps Guide](minima/MINIDAPPS.md) | Serverless dapp infrastructure |
| [MxID Specification](minima/MXID.md) | Stable identity system |
| [Backup & Restore](minima/BACKUP.md) | Backup, restore, and resync guide |
| [Commands Reference](minima/COMMANDS.md) | Full RPC command list |

## Agent Quickstart

**1. Run node:** `./minima/start.sh`

**2. Back up immediately:** `./minima/cli.sh vault` (view seed phrase)

**3. Initialize MxID:** `./minima/mxid_init.sh` (stable identity)

**4. Explore MDS:** `./minima/mds_list.sh --table` (view MiniDapps)

**5. Get Maxima address:** `./minima/get_maxima.sh`

**6. Send value:** `./minima/cli.sh send address:MxG... amount:1`

**7. Add contact:** `./minima/cli.sh maxcontacts action:add contact:MxG...@IP:PORT`

**8. Send message:** `./minima/cli.sh maxima action:send to:MxG... application:app data:hello`

See [AGENT_QUICKSTART.md](minima/AGENT_QUICKSTART.md) for full details.

## MxID - Stable Agent Identity

MxID is a reachable, stable identity that survives restarts, IP changes, and address rotation.

**Prerequisites:** `jq` installed

### Quick Setup (Wizard)
```bash
./minima/mxid_init.sh
```

The wizard auto-detects if your node can be its own MLS (public IP + port listening) and guides you through the entire setup.

### Manual Setup
```bash
./minima/mxid_setup_mls.sh          # 1. Set Static MLS
./minima/mxid_register_permanent.sh  # 2. Register Permanent MAX#
./minima/mxid_lockdown_contacts.sh   # 3. Lock down contacts
./minima/mxid_claim.sh               # 4. Claim MxID
```

### Identity Primitives
```bash
./minima/mxid_info.sh       # Identity card (JSON)
./minima/mxid_challenge.sh  # Generate verification challenge
./minima/mxid_sign.sh       # Sign data
./minima/mxid_verify.sh     # Verify signature
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
COMMUNITY_MLS_HOST="Mx...@1.2.3.4:9001" ./minima/mxid_init.sh  # Fallback MLS
AUTO_DETECT_MLS=false ./minima/mxid_init.sh                    # Force manual
```

### Graduation to Sovereignty

If you start with community MLS, the wizard prints a single command to upgrade later:
```bash
./minima/cli.sh maxextra action:staticmls host:$(./minima/cli.sh maxima | jq -r '.response.p2pidentity')
```

After switching, re-register your Permanent MAX# on the new MLS.

Once claimed, publish: `"I'm MxID verified. MAX#0x3081...#Mx...@IP:PORT"`

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
| `mds_store.sh` | Add/list/browse community MiniDapp stores |

See [MINIDAPPS.md](minima/MINIDAPPS.md) for detailed MiniDapp documentation and community store directory.

## MxID Scripts Reference

| Script | Purpose |
|--------|---------|
| `mxid_init.sh` | Full wizard with auto-detection |
| `mxid_setup_mls.sh` | Set Static MLS host |
| `mxid_register_permanent.sh` | Register Permanent MAX# |
| `mxid_lockdown_contacts.sh` | Disable unsolicited contacts |
| `mxid_claim.sh` | Claim and print MxID |
| `mxid_info.sh` | Output identity card (JSON) |
| `mxid_challenge.sh` | Generate 32-byte challenge |
| `mxid_sign.sh` | Sign data with Maxima key |
| `mxid_verify.sh` | Verify signature |
