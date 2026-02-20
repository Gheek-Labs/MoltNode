"""
Minima Python Bot Template

Periodic balance and status monitor using the Python integration kit.
Shows the correct way to read and display Minima balances.

Usage:
    python bot.py                 # Run with defaults
    INTERVAL=30 python bot.py     # Check every 30 seconds
"""

import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'integration', 'python'))
from minima_client import MinimaClient, MinimaError, MinimaConnectionError


INTERVAL = int(os.environ.get('INTERVAL', '60'))
ALERT_THRESHOLD = float(os.environ.get('ALERT_THRESHOLD', '0'))


def print_header():
    print("=" * 60)
    print("  Minima Bot — Balance & Status Monitor")
    print("=" * 60)
    print()


def print_status(client):
    status = client.status()
    print(f"  Version:  {status['version']}")
    print(f"  Block:    {status['block']:,}")
    print(f"  Height:   {status['chain_height']:,}")
    print(f"  Devices:  {status['devices']}")
    print(f"  Mempool:  {status['mempool']}")
    print(f"  Time:     {status['uptime']}")


def print_balance(client):
    """
    Display wallet balances using the correct fields.

    - sendable:    What you can spend right now (PRIMARY)
    - confirmed:   Full wallet balance including locked coins
    - unconfirmed: Pending incoming
    - coins:       Number of UTXOs

    NEVER use supply.total as a balance — it's the token hardcap.
    """
    balances = client.balance()

    if not balances:
        print("  No balances found.")
        return

    for b in balances:
        name = b['token'] or b['tokenid'][:12] + '...'
        print(f"\n  Token: {name} ({b['tokenid'][:12]}...)")
        print(f"    Sendable:    {b['sendable']:>20}  <- spendable now")
        print(f"    Confirmed:   {b['confirmed']:>20}  <- full balance (includes locked)")
        print(f"    Unconfirmed: {b['unconfirmed']:>20}  <- pending")
        print(f"    Coins:       {b['coins']:>20}  <- UTXO count")

        sendable = float(b['sendable'])
        if ALERT_THRESHOLD > 0 and sendable < ALERT_THRESHOLD:
            print(f"    *** ALERT: Sendable below threshold ({ALERT_THRESHOLD}) ***")


def print_address(client):
    addr = client.getaddress()
    print(f"  Address:  {addr['miniaddress']}")


def run_check(client):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'—' * 60}")
    print(f"  Check at {timestamp}")
    print(f"{'—' * 60}")

    try:
        print("\n[Status]")
        print_status(client)
    except MinimaError as e:
        print(f"  Status error: {e}")

    try:
        print("\n[Balance]")
        print_balance(client)
    except MinimaError as e:
        print(f"  Balance error: {e}")

    try:
        print("\n[Address]")
        print_address(client)
    except MinimaError as e:
        print(f"  Address error: {e}")


def main():
    print_header()

    host = os.environ.get('MINIMA_HOST', 'localhost')
    port = int(os.environ.get('MINIMA_PORT', '9005'))
    client = MinimaClient(host=host, port=port)

    print(f"  Target:   {host}:{port}")
    print(f"  Interval: {INTERVAL}s")
    if ALERT_THRESHOLD > 0:
        print(f"  Alert:    below {ALERT_THRESHOLD} sendable")
    print()

    while True:
        try:
            run_check(client)
        except MinimaConnectionError as e:
            print(f"\n  CONNECTION FAILED: {e}")
            print(f"  Retrying in {INTERVAL}s...")
        except KeyboardInterrupt:
            print("\n\nBot stopped.")
            break

        try:
            time.sleep(INTERVAL)
        except KeyboardInterrupt:
            print("\n\nBot stopped.")
            break


if __name__ == '__main__':
    main()
