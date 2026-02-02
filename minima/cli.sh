#!/bin/bash

RPC_PORT=9005
RPC_URL="http://localhost:$RPC_PORT"

if [ -z "$1" ]; then
    echo "Minima CLI - Agent-Friendly Interface"
    echo "======================================="
    echo ""
    echo "Usage: ./cli.sh <command>"
    echo ""
    echo "=== Node Info ==="
    echo "  status           - Node status and sync info"
    echo "  block            - Current top block"
    echo "  network          - Network status"
    echo "  burn             - Burn metrics"
    echo ""
    echo "=== Wallet ==="
    echo "  balance          - Token balances"
    echo "  coins            - List coins (relevant:true sendable:true)"
    echo "  keys             - Wallet keys"
    echo "  getaddress       - Get default address"
    echo "  newaddress       - Create new address"
    echo "  tokens           - List tokens"
    echo ""
    echo "=== Transactions ==="
    echo "  send address:0x.. amount:1  - Send Minima"
    echo "  history          - Transaction history"
    echo "  txpow            - Search TxPoW"
    echo ""
    echo "=== Maxima Messaging ==="
    echo "  maxima action:info     - Maxima info (includes current address)"
    echo "  maxcontacts action:list - Contact list"
    echo ""
    echo "Quick: ./get_maxima.sh   - Get current Maxima address directly"
    echo ""
    echo "=== Backup/Restore ==="
    echo "  backup           - Backup system"
    echo "  restore file:    - Restore system"
    echo ""
    echo "  help             - Full command list"
    echo ""
    exit 0
fi

COMMAND="$*"
ENCODED_CMD=$(echo "$COMMAND" | sed 's/ /%20/g')

RESPONSE=$(curl -s "${RPC_URL}/${ENCODED_CMD}" 2>/dev/null)

if [ $? -ne 0 ] || [ -z "$RESPONSE" ]; then
    echo "Error: Cannot connect to Minima node on port $RPC_PORT"
    echo "Make sure the node is running."
    exit 1
fi

echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
