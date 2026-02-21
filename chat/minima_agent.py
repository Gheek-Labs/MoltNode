import subprocess
import json
import os
import re
import sys
import shlex
from typing import Dict, Any, Optional, List, Tuple

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "minima")
INTEGRATION_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "integration", "python")

sys.path.insert(0, INTEGRATION_DIR)
from minima_client import MinimaClient, MinimaError, MinimaConnectionError

_client = MinimaClient()

SAFE_COMMANDS = frozenset([
    "status", "balance", "block", "network", "coins", "keys", "getaddress",
    "history", "maxima", "maxcontacts", "mxid_info", "get_maxima", "mds",
    "peers", "help", "txpow", "tokens", "nfts", "random", "hash",
    "webhooks", "mxid_challenge", "mxid_sign", "mxid_verify",
    "scripts", "newaddress",
])

REQUIRES_CONFIRMATION = frozenset([
    "send", "backup", "vault", "record_onchain",
    "webhooks_clear", "webhooks_remove",
    "mds_install", "mds_remove",
    "maxcontacts_remove",
])

SYSTEM_PROMPT = """You are a helpful assistant that controls a Minima blockchain node. You translate natural language requests into node commands and explain results in plain English.

## How Commands Work

When you need to run a command, output it in this exact format on its own line:
[EXECUTE: command_here]

For example:
[EXECUTE: status]
[EXECUTE: balance]
[EXECUTE: maxima action:info]

## Available Commands

### Node Info (Safe - run automatically)
- `status` - Node status, sync info, version, connections, uptime
- `balance` - Token balances (use `sendable` as primary balance, NEVER use `total`)
- `balance tokendetails:true` - Balances with token metadata (decimals, scale, script)
- `tokens` - List all known tokens with supply info
- `nfts` - List NFTs in wallet (tokens with decimals=0)
- `block` - Current top block
- `network` - Network status
- `coins` - List coins/UTXOs
- `keys` - Wallet keys
- `getaddress` - Get default receive address
- `newaddress` - Generate a new address
- `history` - Transaction history
- `peers` - Connected peers
- `scripts` - List registered scripts
- `random` - Generate 256-bit cryptographic random value
- `hash data:<DATA>` - Compute Keccak-256 hash (LOCAL only, does NOT write to blockchain)
- `help` - List all available RPC commands

### Maxima Messaging (Safe)
- `maxima action:info` - Your Maxima identity (contact address, public key, MLS)
- `maxcontacts action:list` - List contacts
- `maxcontacts action:add contact:<ADDRESS>` - Add a contact

### MxID Identity (Safe)
- `mxid_info` - Get your MxID identity card (JSON)
- `get_maxima` - Get current Maxima address
- `mxid_challenge` - Generate a verification challenge (32-byte random)
- `mxid_sign data:<HEX_DATA>` - Sign data with your Maxima key
- `mxid_verify data:<HEX_DATA> signature:<SIG> publickey:<KEY>` - Verify a signature

### MDS MiniDapps (Safe)
- `mds` - MDS status
- `mds action:list` - List installed MiniDapps

### Webhooks (Safe to query)
- `webhooks action:list` - List registered webhooks

### On-Chain Records (REQUIRES CONFIRMATION)
- `record_onchain data:<TEXT>` - Post permanent data on-chain (returns txpowid)
- `record_onchain data:<TEXT> port:<N>` - Use custom state port (0-254)
- `record_onchain data:<TEXT> burn:<AMOUNT>` - Add priority fee

### Transactions (REQUIRES CONFIRMATION)
- `send address:<ADDRESS> amount:<AMOUNT>` - Send Minima
- `send address:<ADDRESS> amount:<AMOUNT> tokenid:<TOKENID>` - Send tokens
- `send address:<ADDRESS> amount:<AMOUNT> split:<N>` - Send and split into N coins (1-10)

#### Splitting UTXOs (Coins)
The `split:` parameter divides the sent amount into multiple equal coins (1-10 max).
- To split your own coins: send to your own address with split:N
- Example: `send address:MxG0123... amount:10 split:5` creates 5 coins of 2 Minima each

When user asks to split their own coins:
1. Run [EXECUTE: getaddress] silently to get their address
2. Immediately construct the send command with that address
3. Present ONE confirmation message with all details

When user wants to send, present a SINGLE concise confirmation:
"Send <AMOUNT> Minima to <ADDRESS> (split into <N> coins)? Type confirm or cancel."
Do NOT show intermediate steps or the raw getaddress result.

### Webhook Management (REQUIRES CONFIRMATION for remove/clear)
- `webhooks_clear` - Clear all webhooks
- `webhooks_remove hook:<URL>` - Remove a specific webhook

### MDS Management (REQUIRES CONFIRMATION)
- `mds_install url:<URL>` - Install a MiniDapp from URL
- `mds_remove uid:<UID>` - Remove an installed MiniDapp

### Contact Management (REQUIRES CONFIRMATION for remove)
- `maxcontacts_remove id:<ID>` - Remove a contact

### Sensitive (REQUIRES CONFIRMATION)
- `vault` - View seed phrase (VERY sensitive!)
- `backup` - Create backup

For vault/backup, ask user to explicitly confirm they want to see/create it.

## BALANCE SEMANTICS — CRITICAL

When displaying balances, you MUST follow these rules:

| Field | Meaning | How to display |
|-------|---------|---------------|
| `sendable` | Spendable right now | **PRIMARY BALANCE — always show this** |
| `confirmed` | Full wallet (includes locked) | Show as "full balance" if different from sendable |
| `unconfirmed` | Pending incoming | Show as "pending" if > 0 |
| `coins` | Number of UTXOs | Mention only if user asks |
| `total` | Token MAX SUPPLY (~1 billion) | **NEVER display as balance** |

Example: If sendable=95, confirmed=100, unconfirmed=5 → say "You have 95 Minima available to send (100 total in wallet, 5 pending confirmation)."
If sendable=0, confirmed=0 → say "Your wallet is empty."

## hash vs on-chain record

The `hash` command computes a LOCAL hash. It does NOT write to the blockchain and does NOT return a txpowid.
To create an on-chain record, use `record_onchain` which posts a real transaction and returns a txpowid.

## Project Templates

This project includes ready-made templates in the `templates/` directory:

### 1. ROS2 Bridge Skeleton (`templates/ros2-bridge/`)
A skeleton for bridging Minima RPC data into ROS2 topics. It publishes node status, wallet balances, and addresses as ROS2 messages.
- **Message types:** MinimaBalance.msg, MinimaStatus.msg, MinimaAddress.msg
- **Topics:** `/minima/balance` (0.1 Hz), `/minima/status` (0.1 Hz), `/minima/address` (on startup)
- **Setup:** Place in a ROS2 workspace `src/` directory, copy the Python SDK (`integration/python/minima_client.py`) into the package, then `colcon build` and `ros2 run`
- **Key file:** `minima_bridge_node.py` — a ROS2 node that uses MinimaClient to poll balance/status and publish to topics
- Balance warning: publishes `sendable` as primary balance, never `total` (which is token max supply)

### 2. Node.js Web Dashboard (`templates/node-web-dashboard/`)
An Express.js dashboard that displays balance (3-field: sendable/confirmed/unconfirmed), status, and recent blocks. Uses the Node.js SDK.

### 3. Node.js Webhook Listener (`templates/node-webhook-listener/`)
A zero-dependency Node.js HTTP server that listens for Minima webhook events (NEWBLOCK, MINING, MDS_TIMER). Registers itself on startup, logs events, and handles graceful shutdown.

### 4. Python Bot (`templates/python-bot/`)
A CLI-based balance and status monitor using the Python SDK. Polls periodically and prints formatted output.

When users ask about templates, ROS2, dashboards, webhook listeners, or bot examples, describe these templates and explain how to use them.

## Response Format

1. Determine what command(s) to run based on user request
2. For safe commands: output [EXECUTE: command] and wait for results
3. For confirmation-required commands: ask for confirmation first, only execute after user says yes/confirm
4. Explain results in plain, friendly English
5. Format balances using the rules above — always prioritize `sendable`

## Security Rules

- For send/vault/backup/record_onchain: ALWAYS ask for confirmation first, never auto-execute
- For webhooks_clear/remove, mds_install/remove, maxcontacts_remove: ask for confirmation
- When confirming a send, repeat the exact amount and address back to user
- Never reveal private keys unless vault is explicitly requested and confirmed
"""


def execute_command(command: str) -> Dict[str, Any]:
    """Execute a Minima command using the SDK or shell scripts."""
    try:
        parts = command.split()
        base = parts[0].lower().strip() if parts else ""
        params = _parse_params(command)

        if base == "mxid_info":
            return _run_script("mxid_info.sh")

        elif base == "get_maxima":
            result = _run_script("get_maxima.sh")
            if result.get("status") and isinstance(result.get("response"), str):
                return {"status": True, "response": {"address": result["response"].strip()}}
            return result

        elif base == "mxid_challenge":
            return _run_script("mxid_challenge.sh")

        elif base == "mxid_sign":
            data = params.get("data", "")
            if not data:
                return {"status": False, "error": "Missing data parameter. Usage: mxid_sign data:<hex>"}
            return _run_script("mxid_sign.sh", [data])

        elif base == "mxid_verify":
            data = params.get("data", "")
            sig = params.get("signature", "")
            pubkey = params.get("publickey", "")
            if not all([data, sig, pubkey]):
                return {"status": False, "error": "Missing parameters. Usage: mxid_verify data:<hex> signature:<sig> publickey:<key>"}
            return _run_script("mxid_verify.sh", [data, sig, pubkey])

        elif base == "mxid_claim":
            return {"status": False, "error": "mxid_claim is interactive and cannot be run via chat. Use the terminal."}

        elif base == "nfts":
            nfts = _client.nfts()
            return {"status": True, "response": nfts}

        elif base == "tokens":
            tokens = _client.tokens()
            return {"status": True, "response": tokens}

        elif base == "random":
            rnd = _client.random()
            return {"status": True, "response": rnd}

        elif base == "record_onchain":
            data = params.get("data", "")
            if not data:
                return {"status": False, "error": "Missing data parameter. Usage: record_onchain data:<text>"}
            port = int(params.get("port", "0"))
            burn_str = params.get("burn")
            burn = float(burn_str) if burn_str else None
            result = _client.record_onchain(data, port=port, burn=burn)
            return {"status": True, "response": result}

        elif base == "webhooks_clear":
            result = _client.command("webhooks action:clear")
            return result

        elif base == "webhooks_remove":
            hook = params.get("hook", "")
            if not hook:
                return {"status": False, "error": "Missing hook URL. Usage: webhooks_remove hook:<url>"}
            result = _client.command(f"webhooks action:remove hook:{hook}")
            return result

        elif base == "mds_install":
            url = params.get("url", "")
            if not url:
                return {"status": False, "error": "Missing URL. Usage: mds_install url:<url>"}
            return _run_script("mds_install.sh", [url])

        elif base == "mds_remove":
            uid = params.get("uid", "")
            if not uid:
                return {"status": False, "error": "Missing UID. Usage: mds_remove uid:<uid>"}
            result = _client.command(f"mds action:remove uid:{uid}")
            return result

        elif base == "maxcontacts_remove":
            contact_id = params.get("id", "")
            if not contact_id:
                return {"status": False, "error": "Missing contact ID. Usage: maxcontacts_remove id:<id>"}
            result = _client.command(f"maxcontacts action:remove id:{contact_id}")
            return result

        elif command.startswith("balance"):
            if "tokendetails" in command:
                bal = _client.balance(token_details=True)
            else:
                bal = _client.balance()
            return {"status": True, "response": bal}

        elif base == "hash":
            data = params.get("data", "")
            if not data:
                return {"status": False, "error": "Missing data parameter. Usage: hash data:<text>"}
            result = _client.hash(data)
            return {"status": True, "response": result}

        elif base == "getaddress":
            addr = _client.getaddress()
            return {"status": True, "response": addr}

        elif base == "newaddress":
            result = _client.command("newaddress")
            return result

        elif base == "status":
            stat = _client.status()
            return {"status": True, "response": stat}

        elif base == "maxima":
            if "info" in command:
                info = _client.maxima_info()
                return {"status": True, "response": info}
            else:
                result = _client.command(command)
                return result

        elif base == "maxcontacts":
            if "list" in command:
                contacts = _client.contacts()
                return {"status": True, "response": contacts}
            else:
                result = _client.command(command)
                return result

        elif base == "send":
            address = params.get("address", "")
            amount = params.get("amount", "")
            tokenid = params.get("tokenid")
            split_str = params.get("split")
            burn_str = params.get("burn")
            split = int(split_str) if split_str else None
            burn = float(burn_str) if burn_str else None
            result = _client.send(address, amount, tokenid=tokenid, split=split, burn=burn)
            return {"status": True, "response": result}

        elif base == "webhooks":
            result = _client.command(command)
            return result

        elif base == "mds":
            result = _client.command(command)
            return result

        else:
            return {"status": False, "error": f"Unknown command: {base}. Use 'help' to see available commands."}

    except MinimaConnectionError as e:
        return {"status": False, "error": f"Node not reachable: {e}. Is the Minima node running?"}
    except MinimaError as e:
        return {"status": False, "error": f"Command failed: {e}"}
    except Exception as e:
        return {"status": False, "error": str(e)}


def _parse_params(command: str) -> Dict[str, str]:
    """Parse key:value parameters from a command string.
    
    Handles spaces in values by treating the last key: as capturing
    everything until the next key: or end of string.
    Example: 'record_onchain data:hello world port:0' -> {'data': 'hello world', 'port': '0'}
    """
    params = {}
    parts = command.split(None, 1)
    if len(parts) < 2:
        return params
    rest = parts[1]
    tokens = re.findall(r'(\w+):(.*?)(?=\s+\w+:|$)', rest, re.DOTALL)
    for key, value in tokens:
        params[key] = value.strip()
    return params


def _run_script(script_name: str, args: List[str] = None) -> Dict[str, Any]:
    """Run a shell script from the minima directory."""
    script_path = os.path.join(SCRIPT_DIR, script_name)
    cmd_args = [script_path] + (args or [])
    try:
        result = subprocess.run(
            cmd_args,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(SCRIPT_DIR),
        )
        if result.returncode == 0:
            try:
                return {"status": True, "response": json.loads(result.stdout)}
            except json.JSONDecodeError:
                return {"status": True, "response": result.stdout.strip()}
        return {"status": False, "error": result.stderr or result.stdout or "Script failed"}
    except subprocess.TimeoutExpired:
        return {"status": False, "error": "Command timed out"}
    except Exception as e:
        return {"status": False, "error": str(e)}


def extract_command_base(command: str) -> str:
    """Extract the base command name from a command string."""
    parts = command.split()
    return parts[0] if parts else ""


def is_safe_command(command: str) -> bool:
    """Check if a command is safe to execute without confirmation."""
    base = extract_command_base(command).lower().strip()
    if base in SAFE_COMMANDS:
        return True
    if base == "balance":
        return True
    return False


DESTRUCTIVE_RPC_PATTERNS = [
    r'^webhooks\s+action:clear',
    r'^webhooks\s+action:remove',
    r'^mds\s+action:remove',
    r'^mds\s+action:install',
    r'^maxcontacts\s+action:remove',
]


def requires_confirmation(command: str) -> bool:
    """Check if a command requires explicit user confirmation."""
    base = extract_command_base(command).lower().strip()
    if base in REQUIRES_CONFIRMATION:
        return True
    for pattern in DESTRUCTIVE_RPC_PATTERNS:
        if re.match(pattern, command, re.IGNORECASE):
            return True
    return False


def format_command_result(command: str, result: Dict[str, Any]) -> str:
    """Format command result for inclusion in chat context."""
    return f"Command: {command}\nResult: {json.dumps(result, indent=2)}"


def extract_commands_from_response(response: str) -> List[str]:
    """Extract commands from LLM response using structured format."""
    pattern = r'\[EXECUTE:\s*(.+?)\]'
    matches = re.findall(pattern, response, re.IGNORECASE)
    return [m.strip() for m in matches]


class MinimaAgent:
    """Agent that uses an LLM to interpret natural language and control Minima node."""

    def __init__(self, provider):
        self.provider = provider
        self.conversation_history = []
        self.pending_confirmation = None

    def chat(self, user_message: str) -> str:
        """Process a user message and return a response."""
        user_lower = user_message.lower().strip()

        if self.pending_confirmation and user_lower in ["yes", "confirm", "ok", "proceed", "do it", "send it"]:
            cmd = self.pending_confirmation
            self.pending_confirmation = None

            result = execute_command(cmd)
            self.conversation_history.append({"role": "user", "content": user_message})

            if result.get("status"):
                res = result.get("response", result)
                if isinstance(res, dict) and "txpowid" in res:
                    txid = res.get("txpowid", "")
                    explorer_url = res.get("explorer_url", f"https://explorer.minima.global/transactions/{txid}")
                    response = f"Done!\n\n**TX ID:** `{txid[:20]}...`\n\n[View on Explorer]({explorer_url})\n\n<details>\n<summary>View full response</summary>\n\n```json\n{json.dumps(res, indent=2)}\n```\n</details>"
                else:
                    response = f"Done!\n\n<details>\n<summary>View response</summary>\n\n```json\n{json.dumps(res, indent=2)}\n```\n</details>"
            else:
                response = f"Command failed: {result.get('error', 'Unknown error')}"

            self.conversation_history.append({"role": "assistant", "content": response})
            return response

        elif self.pending_confirmation and user_lower in ["no", "cancel", "abort", "nevermind", "stop"]:
            self.pending_confirmation = None
            self.conversation_history.append({"role": "user", "content": user_message})
            response = "OK, cancelled. The command was not executed."
            self.conversation_history.append({"role": "assistant", "content": response})
            return response

        self.pending_confirmation = None

        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        response = self.provider.chat(
            messages=self.conversation_history,
            system_prompt=SYSTEM_PROMPT
        )

        commands = extract_commands_from_response(response)
        executed_results = []
        blocked_commands = []

        for cmd in commands:
            if requires_confirmation(cmd):
                blocked_commands.append(cmd)
                self.pending_confirmation = cmd
            elif is_safe_command(cmd):
                result = execute_command(cmd)
                executed_results.append((cmd, result))

        if executed_results:
            context = "\n\n[SYSTEM: I executed the following commands. Now provide a friendly summary of the results. Remember: for balances, always use `sendable` as the primary balance. NEVER report `total` as balance — it is the token max supply (~1 billion).]\n"
            for cmd, result in executed_results:
                context += format_command_result(cmd, result) + "\n"

            self.conversation_history.append({"role": "assistant", "content": response})
            self.conversation_history.append({"role": "user", "content": context})

            final_response = self.provider.chat(
                messages=self.conversation_history,
                system_prompt=SYSTEM_PROMPT
            )
        elif blocked_commands:
            has_confirmation = any(word in response.lower() for word in ["confirm", "cancel", "proceed", "abort"])
            if has_confirmation:
                final_response = response
            else:
                cmd = blocked_commands[0]
                final_response = f"{response}\n\n**Confirm:** `{cmd}` - Type **confirm** or **cancel**."
        else:
            final_response = response

        self.conversation_history.append({
            "role": "assistant",
            "content": final_response
        })

        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return final_response

    def reset(self):
        """Clear conversation history and pending confirmations."""
        self.conversation_history = []
        self.pending_confirmation = None
