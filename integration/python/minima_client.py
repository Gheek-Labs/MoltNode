"""
Minima RPC Client for Python

Safe, typed interface to a Minima node's RPC endpoint.
Normalizes responses so the default API path prevents common mistakes.

Usage:
    from minima_client import MinimaClient

    client = MinimaClient()           # default: localhost:9005
    bal = client.balance()            # normalized, no 'total' trap
    status = client.status()
    tx = client.send("MxG08...", 1)   # returns tx with explorer link
"""

import json
import time
import urllib.request
import urllib.parse
import urllib.error


class MinimaError(Exception):
    """Raised when an RPC command returns status=false."""
    pass


class MinimaConnectionError(Exception):
    """Raised when the node is unreachable after retries."""
    pass


class MinimaClient:
    """HTTP client for Minima RPC with retries and normalized responses."""

    def __init__(self, host="localhost", port=9005, retries=3, retry_delay=1.0):
        self.base_url = f"http://{host}:{port}"
        self.retries = retries
        self.retry_delay = retry_delay

    def command(self, cmd):
        """
        Execute a raw RPC command. Returns the parsed JSON response.

        Args:
            cmd: RPC command string (e.g., "balance", "send address:MxG.. amount:1")

        Returns:
            dict: Full parsed JSON response {"status": bool, "response": ...}

        Raises:
            MinimaError: When status is false
            MinimaConnectionError: When node is unreachable after retries
        """
        encoded = urllib.parse.quote(cmd, safe="")
        url = f"{self.base_url}/{encoded}"

        last_error = None
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read().decode("utf-8")
                    result = json.loads(raw)

                    if not result.get("status", False):
                        raise MinimaError(result.get("error", "Unknown RPC error"))

                    return result

            except (urllib.error.URLError, ConnectionError, OSError) as e:
                last_error = e
                if attempt < self.retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))

        raise MinimaConnectionError(
            f"Failed to connect to {self.base_url} after {self.retries} attempts: {last_error}"
        )

    def balance(self, tokenid=None):
        """
        Get wallet balances with safe field naming.

        The dangerous 'total' field (token max supply) is moved to
        supply.total so it cannot be confused with wallet balance.

        Args:
            tokenid: Optional token ID filter (e.g., "0x00" for Minima)

        Returns:
            list[dict]: Normalized balances, each with:
                - token (str): Token display name
                - tokenid (str): Token identifier
                - sendable (str): Available to spend — PRIMARY BALANCE
                - confirmed (str): Full wallet balance (includes locked)
                - unconfirmed (str): Pending incoming
                - coins (str): Number of UTXOs
                - supply (dict): {"total": str} — token max supply, NOT balance
        """
        result = self.command("balance")
        entries = result.get("response", [])

        normalized = []
        for entry in entries:
            item = {
                "token": entry.get("token", ""),
                "tokenid": entry.get("tokenid", ""),
                "sendable": entry.get("sendable", "0"),
                "confirmed": entry.get("confirmed", "0"),
                "unconfirmed": entry.get("unconfirmed", "0"),
                "coins": entry.get("coins", "0"),
                "supply": {
                    "total": entry.get("total", "0"),
                },
            }
            normalized.append(item)

        if tokenid:
            normalized = [b for b in normalized if b["tokenid"] == tokenid]

        return normalized

    def balance_summary(self, tokenid="0x00"):
        """
        Get a simple balance summary for one token.

        Returns:
            dict: {sendable, confirmed, unconfirmed, coins} as floats
        """
        balances = self.balance(tokenid=tokenid)
        if not balances:
            return {"sendable": 0.0, "confirmed": 0.0, "unconfirmed": 0.0, "coins": 0}

        b = balances[0]
        return {
            "sendable": float(b["sendable"]),
            "confirmed": float(b["confirmed"]),
            "unconfirmed": float(b["unconfirmed"]),
            "coins": int(b["coins"]),
        }

    def status(self):
        """
        Get node status with numeric fields parsed.

        Returns:
            dict: Normalized status with parsed integers where appropriate:
                - version (str)
                - chain_height (int): Parsed from response.length
                - block (int): Current block number
                - devices (int)
                - mempool (int): Pending transactions
                - uptime (str): Human-readable date
                - raw (dict): Full unmodified response
        """
        result = self.command("status")
        resp = result.get("response", {})
        chain = resp.get("chain", {})
        txpow = resp.get("txpow", {})

        return {
            "version": resp.get("version", ""),
            "chain_height": _safe_int(resp.get("length", "0")),
            "block": _safe_int(chain.get("block", "0")),
            "devices": _safe_int(resp.get("devices", "0")),
            "mempool": _safe_int(txpow.get("mempool", "0")),
            "uptime": chain.get("date", ""),
            "raw": resp,
        }

    def send(self, address, amount, tokenid=None, split=None, burn=None):
        """
        Send Minima or tokens to an address.

        Args:
            address: Destination (MxG... or 0x...)
            amount: Amount to send
            tokenid: Token ID (default: 0x00 for native Minima)
            split: Split into N output coins (1-10)
            burn: Burn amount as fee

        Returns:
            dict: {txpowid, explorer_url, block, date, raw}
        """
        cmd = f"send address:{address} amount:{amount}"
        if tokenid:
            cmd += f" tokenid:{tokenid}"
        if split:
            cmd += f" split:{split}"
        if burn:
            cmd += f" burn:{burn}"

        result = self.command(cmd)
        resp = result.get("response", {})
        txpowid = resp.get("txpowid", "")

        return {
            "txpowid": txpowid,
            "explorer_url": f"https://explorer.minima.global/transactions/{txpowid}",
            "block": resp.get("header", {}).get("block", ""),
            "date": resp.get("header", {}).get("date", ""),
            "raw": resp,
        }

    def hash(self, data):
        """
        Hash data using Minima's Keccak-256.

        Args:
            data: String or 0x-prefixed hex data

        Returns:
            dict: {input, hash}
        """
        result = self.command(f"hash data:{data}")
        resp = result.get("response", {})
        return {
            "input": resp.get("input", ""),
            "hash": resp.get("hash", ""),
        }

    def random(self):
        """
        Generate 256-bit cryptographic random value.

        Returns:
            str: 0x-prefixed random hex string
        """
        result = self.command("random")
        return result.get("response", {}).get("random", "")

    def tokens(self):
        """
        List all tokens known to this node.

        Returns:
            list[dict]: Each with {tokenid, name, supply_total, decimals, scale}
                        Note: supply_total is token max supply, NOT wallet balance.
        """
        result = self.command("tokens")
        entries = result.get("response", [])

        normalized = []
        for entry in entries:
            token = entry.get("token", "")
            name = token if isinstance(token, str) else token.get("name", str(token))

            normalized.append({
                "tokenid": entry.get("tokenid", ""),
                "name": name,
                "supply_total": entry.get("total", "0"),
                "decimals": _safe_int(entry.get("decimals", "0")),
                "scale": _safe_int(entry.get("scale", "0")),
            })

        return normalized

    def getaddress(self):
        """
        Get the node's default receiving address.

        Returns:
            dict: {address, miniaddress, publickey}
        """
        result = self.command("getaddress")
        resp = result.get("response", {})
        return {
            "address": resp.get("address", ""),
            "miniaddress": resp.get("miniaddress", ""),
            "publickey": resp.get("publickey", ""),
        }

    def maxima_info(self):
        """
        Get Maxima identity and contact details.

        Returns:
            dict: {name, publickey, mls, p2pidentity, localidentity, contact}
        """
        result = self.command("maxima action:info")
        resp = result.get("response", {})
        return {
            "name": resp.get("name", ""),
            "publickey": resp.get("publickey", ""),
            "mls": resp.get("mls", ""),
            "p2pidentity": resp.get("p2pidentity", ""),
            "localidentity": resp.get("localidentity", ""),
            "contact": resp.get("contact", ""),
        }

    def contacts(self):
        """
        List Maxima contacts.

        Returns:
            list[dict]: Each with {id, name, publickey, address, lastseen, samechain}
        """
        result = self.command("maxcontacts action:list")
        entries = result.get("response", [])

        normalized = []
        for entry in entries:
            extra = entry.get("extradata", {})
            normalized.append({
                "id": entry.get("id", 0),
                "name": extra.get("name", ""),
                "publickey": entry.get("publickey", ""),
                "address": entry.get("currentaddress", ""),
                "lastseen": entry.get("date", ""),
                "samechain": entry.get("samechain", False),
            })

        return normalized


def _safe_int(val):
    """Safely parse a string to int, returning 0 on failure."""
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0
