import subprocess
import json
import os
import re
import shlex
from typing import Dict, Any, Optional, List, Tuple

SCRIPT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "minima")

# Safe commands that can be executed without confirmation
SAFE_COMMANDS = frozenset([
    "status", "balance", "block", "network", "coins", "keys", "getaddress",
    "history", "maxima", "maxcontacts", "mxid_info", "get_maxima", "mds",
    "peers", "help", "txpow"
])

# Commands that require explicit user confirmation (handled via confirmation flow)
REQUIRES_CONFIRMATION = frozenset(["send", "backup", "vault"])

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
- `status` - Node status and sync info
- `balance` - Token balances  
- `block` - Current top block
- `network` - Network status
- `coins` - List coins
- `keys` - Wallet keys
- `getaddress` - Get default address
- `history` - Transaction history
- `peers` - Connected peers

### Maxima Messaging (Safe)
- `maxima action:info` - Your Maxima info (contact address, public key)
- `maxcontacts action:list` - List contacts
- `maxcontacts action:add contact:<ADDRESS>` - Add contact

### MxID (Identity - Safe)
- `mxid_info` - Get your MxID identity card (JSON)
- `get_maxima` - Get current Maxima address

### MDS (MiniDapps - Safe)
- `mds action:list` - List installed MiniDapps

### Transactions (REQUIRES CONFIRMATION)
- `send address:<ADDRESS> amount:<AMOUNT>` - Send Minima
- `send address:<ADDRESS> amount:<AMOUNT> tokenid:<TOKENID>` - Send tokens
- `send address:<ADDRESS> amount:<AMOUNT> split:<N>` - Send and split into N coins (1-20)
- `send multi:["<ADDR1>:<AMT1>","<ADDR2>:<AMT2>"] split:<N>` - Multi-send with split

#### Splitting UTXOs (Coins)
The `split:` parameter divides the sent amount into multiple equal coins (1-20, default 1).
- Useful for parallel spending without waiting for change confirmation
- To split your own coins: send to your own address with split:N
- Example: `send address:0xFF.. amount:10 split:5` creates 5 coins of 2 Minima each
- Multi-send: `send multi:["0xFF..:10","0xEE..:10"] split:20`

When user asks to "split coins" or "prepare for multiple sends", suggest splitting to their own address.

When user wants to send, DO NOT execute directly. Instead:
1. Summarize the transaction: amount, destination, token, split count if used
2. Ask them to confirm by typing "confirm" or similar

### Sensitive (REQUIRES CONFIRMATION)
- `vault` - View seed phrase (VERY sensitive!)
- `backup` - Create backup

For vault/backup, ask user to explicitly confirm they want to see/create it.

## Response Format

1. Determine what command(s) to run based on user request
2. For safe commands: output [EXECUTE: command] and wait for results
3. For sensitive commands: ask for confirmation first, only execute after user says yes/confirm
4. Explain results in plain, friendly English

## Response Interpretation

### Balance Command
The balance response contains an array of tokens. For each token, report:
- `token`: Token name (e.g., "Minima")
- `confirmed`: Confirmed balance (spendable)
- `unconfirmed`: Pending incoming balance
- `sendable`: Amount available to send
- `coins`: Number of UTXOs

IMPORTANT: The `total` field is the MAX SUPPLY of the token, NOT the user's balance! Never report `total` as balance.

Example interpretation:
- "confirmed": "100" means you have 100 confirmed Minima
- "sendable": "95" means you can send up to 95 Minima
- "unconfirmed": "5" means 5 Minima is pending confirmation

If all values are "0", tell the user their wallet is empty.

## Security Rules

- For send/vault/backup: ALWAYS ask for confirmation first, never auto-execute
- When confirming a send, repeat the exact amount and address back to user
- Never reveal private keys unless vault is explicitly requested and confirmed
"""

def parse_command(command_str: str) -> List[str]:
    """Safely parse a command string into arguments, handling quoted values."""
    try:
        return shlex.split(command_str)
    except ValueError:
        return command_str.split()


def extract_command_base(command: str) -> str:
    """Extract the base command name (first word) from a command string."""
    parts = command.split()
    return parts[0] if parts else ""


def is_safe_command(command: str) -> bool:
    """Check if a command is safe to execute without confirmation."""
    base = extract_command_base(command)
    return base in SAFE_COMMANDS


def requires_confirmation(command: str) -> bool:
    """Check if a command requires explicit user confirmation."""
    base = extract_command_base(command)
    return base in REQUIRES_CONFIRMATION


def execute_command(command: str) -> Dict[str, Any]:
    """Execute a Minima CLI command and return the result."""
    try:
        if command == "mxid_info":
            result = subprocess.run(
                [os.path.join(SCRIPT_DIR, "mxid_info.sh")],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(SCRIPT_DIR),
            )
            if result.returncode == 0:
                try:
                    return {"status": True, "response": json.loads(result.stdout)}
                except json.JSONDecodeError:
                    return {"status": True, "response": result.stdout}
            return {"status": False, "error": result.stderr or result.stdout}
        
        elif command == "get_maxima":
            result = subprocess.run(
                [os.path.join(SCRIPT_DIR, "get_maxima.sh")],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(SCRIPT_DIR),
            )
            if result.returncode == 0:
                return {"status": True, "response": {"address": result.stdout.strip()}}
            return {"status": False, "error": result.stderr or result.stdout}
        
        elif command == "mxid_claim":
            return {"status": False, "error": "mxid_claim is interactive and cannot be run via chat. Use the terminal."}
        
        else:
            args = parse_command(command)
            result = subprocess.run(
                [os.path.join(SCRIPT_DIR, "cli.sh")] + args,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(SCRIPT_DIR),
            )
            
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                if result.returncode == 0:
                    return {"status": True, "response": result.stdout}
                return {"status": False, "error": result.stderr or result.stdout}
    
    except subprocess.TimeoutExpired:
        return {"status": False, "error": "Command timed out"}
    except Exception as e:
        return {"status": False, "error": str(e)}


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
                response = f"Done! Command executed successfully.\n\nResult: {json.dumps(result.get('response', result), indent=2)}"
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
            context = "\n\n[SYSTEM: I executed the following commands. Now provide a friendly summary of the results.]\n"
            for cmd, result in executed_results:
                context += format_command_result(cmd, result) + "\n"
            
            self.conversation_history.append({"role": "assistant", "content": response})
            self.conversation_history.append({"role": "user", "content": context})
            
            final_response = self.provider.chat(
                messages=self.conversation_history,
                system_prompt=SYSTEM_PROMPT
            )
        elif blocked_commands:
            base = extract_command_base(blocked_commands[0])
            if base == "send":
                final_response = f"I understand you want to execute: `{blocked_commands[0]}`\n\nThis is a transaction that will send funds. Please type **confirm** to proceed, or **cancel** to abort."
            elif base == "vault":
                final_response = "This will reveal your seed phrase which is highly sensitive. Please type **confirm** if you're sure, or **cancel** to abort."
            else:
                final_response = f"This command (`{blocked_commands[0]}`) requires confirmation. Type **confirm** to proceed or **cancel** to abort."
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
