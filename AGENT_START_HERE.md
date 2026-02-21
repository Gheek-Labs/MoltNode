# START HERE — Agent Onboarding

**You must complete the bootstrap sequence below before using any SDKs, templates, chat interface, or advanced features.**

Skipping these steps will result in an unstable node, missing identity, and no backup.

## System Prerequisites

Minima requires these system packages installed **before** bootstrap:

| Package | Purpose | Replit (Nix) | Debian/Ubuntu |
|---------|---------|-------------|---------------|
| **Java (OpenJDK 17+)** | Runs the Minima JAR | `jdk` | `openjdk-17-jre-headless` |
| **jq** | JSON parsing for MxID scripts | `jq` | `jq` |
| **curl** | Downloads JAR and RPC calls | `curl` (usually pre-installed) | `curl` |

**The bootstrap script auto-detects your platform and installs missing dependencies automatically.** It supports apt (Debian/Ubuntu), brew (macOS), dnf (Fedora/RHEL), pacman (Arch), and apk (Alpine). On Replit, Java and jq are pre-installed as Nix system packages.

## Mandatory Bootstrap Sequence

### Step 1: Initialize the node

```bash
./bootstrap.sh
```

This checks prerequisites, downloads the Minima JAR (~70MB on first run), and prepares the environment. If it reports missing dependencies, install them first.

### Step 2: Start the node

```bash
./minima/start.sh
```

Or use the configured "Minima Node" workflow (auto-starts).

**Verify it's running:**

```bash
./minima/cli.sh status
```

Wait until `status: true` and you see a non-zero `chain.block` value. The node needs a few seconds to sync.

### Step 3: Back up immediately

**Do this before anything else. If you lose your seed phrase, everything is unrecoverable.**

```bash
./minima/cli.sh vault
```

Write down the seed phrase. Then create an encrypted backup:

```bash
./minima/cli.sh backup password:YourStrongPassword123
```

### Step 4: Initialize MxID (stable identity)

MxID gives your agent a reachable, stable identity that survives restarts and IP changes.

```bash
./minima/mxid_init.sh
```

The wizard auto-detects your MLS mode (Sovereign, Community, or Manual) and walks you through the full setup.

**Prerequisite:** `jq` must be installed.

### Step 5: Verify peers and connectivity

```bash
./minima/cli.sh peers
./minima/cli.sh network
```

Confirm you have connected peers (typically 2-5). If zero peers, wait a minute — P2P discovery takes time.

---

## You Are Now Ready

Once all 5 steps are complete, your node is bootstrapped, backed up, and has a stable identity. Now you can explore:

| What | Where |
|------|-------|
| Full agent operations guide | [`minima/AGENT_QUICKSTART.md`](minima/AGENT_QUICKSTART.md) |
| Integration SDKs (Node.js + Python) | [`integration/`](integration/) |
| Natural language chat interface | Port 5000 (open webview) |
| On-chain records | [`minima/ONCHAIN_RECORDS.md`](minima/ONCHAIN_RECORDS.md) |
| Webhooks | [`minima/WEBHOOKS.md`](minima/WEBHOOKS.md) |
| MDS MiniDapps | [`minima/MINIDAPPS.md`](minima/MINIDAPPS.md) |
| Templates (dashboard, bot, ROS2, webhook listener) | [`templates/`](templates/) |
| Full RPC command reference | [`minima/COMMANDS.md`](minima/COMMANDS.md) |
| Response schemas (25 commands) | [`minima/RESPONSE_SCHEMAS.md`](minima/RESPONSE_SCHEMAS.md) |
| Agent integration skill (for Replit Agent) | [`.agents/skills/minima-integration/SKILL.md`](.agents/skills/minima-integration/SKILL.md) |

## Network Security

| Port | Service | Binding | Exposure |
|------|---------|---------|----------|
| 9001 | P2P | All interfaces | **Intentionally open** — required for blockchain peer discovery |
| 9003 | MDS | All interfaces (SSL) | Password-protected; block at firewall if not needed externally |
| 9005 | RPC | All interfaces | **No authentication** — must be firewall-restricted in production. On Replit, only port 5000 is externally exposed, so 9005 is safe. On bare metal/VPS, block 9005 at your firewall. |
| 5000 | Chat UI (Flask) | 127.0.0.1 (default) | **Disabled by default.** Requires `ENABLE_CHAT=true` + `CHAT_PASSWORD`. Set `CHAT_BIND=0.0.0.0` for remote access. |

### LLM Privacy Notice
When using the chat interface, full RPC responses (wallet addresses, public keys, balances) are sent to your configured LLM provider as part of conversation context. If using an external provider (OpenAI, Anthropic), this data leaves your machine. For sensitive environments, use a local LLM (Ollama) or the custom provider pointed at a self-hosted endpoint.

## Common Bootstrap Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Java not installed | `java: not found` when starting node | `./bootstrap.sh` auto-installs it; or manually: `apt install openjdk-17-jre-headless` |
| Skipping backup | Seed phrase lost forever if node data corrupted | Run `vault` immediately after first start |
| Skipping MxID | No stable identity; Maxima address rotates every few minutes | Run `mxid_init.sh` after backup |
| Using SDK before node is running | `ECONNREFUSED` on port 9005 | Start node first, verify with `cli.sh status` |
| Displaying `total` as balance | Shows ~1 billion instead of actual balance | Always use `sendable` field |
