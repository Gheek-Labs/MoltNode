#!/bin/bash
#
# Record data on the Minima blockchain.
#
# Posts a self-send transaction with data embedded as state variables.
# Returns the txpowid (on-chain proof) and explorer link.
#
# Usage:
#   ./record_data.sh --data <data> [--port <n>] [--burn <amount>] [--mine]
#
# Examples:
#   ./record_data.sh --data "hello world"
#   ./record_data.sh --data "0x3a7b2c..." --port 1
#   ./record_data.sh --data "0xABCD" --burn 0.001
#   ./record_data.sh --data "0xABCD" --mine
#
# WARNING: hash != on-chain record
#   The 'hash' command is purely local (no txpowid, not on-chain).
#   This script creates an actual on-chain transaction.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RPC_PORT="${RPC_PORT:-9005}"
RPC_URL="http://localhost:${RPC_PORT}"
RECORD_AMOUNT="0.000000001"

DATA=""
PORT=0
BURN=""
MINE=false

show_help() {
    echo "Usage: $0 --data <data> [--port <n>] [--burn <amount>] [--mine]"
    echo ""
    echo "Records data on the Minima blockchain via a self-send transaction."
    echo "Returns txpowid (on-chain proof) and explorer link."
    echo ""
    echo "Options:"
    echo "  --data <data>    String or 0x-prefixed hex to record (REQUIRED)"
    echo "  --port <n>       State variable port number (default: 0)"
    echo "  --burn <amount>  Burn amount for priority fee (optional)"
    echo "  --mine           Mine the transaction immediately (optional)"
    echo ""
    echo "WARNING: 'hash data:...' is a LOCAL operation (not on-chain)."
    echo "         This script creates an actual on-chain record."
    exit 1
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --data)
            DATA="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --burn)
            BURN="$2"
            shift 2
            ;;
        --mine)
            MINE=true
            shift
            ;;
        --help|-h)
            show_help
            ;;
        *)
            if [ -z "$DATA" ]; then
                DATA="$1"
                shift
            else
                echo "Unknown option: $1" >&2
                show_help
            fi
            ;;
    esac
done

if [ -z "$DATA" ]; then
    show_help
fi

TIMESTAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

rpc() {
    local cmd="$1"
    local encoded
    encoded=$(python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=''))" "$cmd" 2>/dev/null || echo "$cmd" | sed 's/ /%20/g; s/{/%7B/g; s/}/%7D/g; s/"/%22/g; s/:/%3A/g; s/,/%2C/g; s/\[/%5B/g; s/\]/%5D/g')
    local response
    response=$(curl -s "${RPC_URL}/${encoded}" 2>/dev/null)

    if [ $? -ne 0 ] || [ -z "$response" ]; then
        echo "Error: Cannot connect to Minima node on port $RPC_PORT" >&2
        exit 1
    fi

    echo "$response"
}

check_jq() {
    if ! command -v jq &>/dev/null; then
        echo "Error: jq is required. Install with: nix-env -iA nixpkgs.jq" >&2
        exit 1
    fi
}

check_jq

ADDRESS=$(rpc "getaddress" | jq -r '.response.miniaddress // empty')
if [ -z "$ADDRESS" ]; then
    echo "Error: Could not get node address. Is the node running?" >&2
    exit 1
fi

STATE_JSON=$(jq -n --arg port "$PORT" --arg data "$DATA" --arg ts "$TIMESTAMP" '{($port): $data, "255": $ts}')

CMD="send address:${ADDRESS} amount:${RECORD_AMOUNT} state:${STATE_JSON}"

if [ -n "$BURN" ]; then
    CMD="${CMD} burn:${BURN}"
fi

if [ "$MINE" = true ]; then
    CMD="${CMD} mine:true"
fi

RESULT=$(rpc "$CMD")

STATUS=$(echo "$RESULT" | jq -r '.status // false')
if [ "$STATUS" != "true" ]; then
    ERROR=$(echo "$RESULT" | jq -r '.error // "Unknown error"')
    echo "Error: Transaction failed — $ERROR" >&2
    exit 1
fi

TXPOWID=$(echo "$RESULT" | jq -r '.response.txpowid // empty')
if [ -z "$TXPOWID" ]; then
    echo "Error: No txpowid in response" >&2
    echo "$RESULT" | jq . >&2
    exit 1
fi

EXPLORER_URL="https://explorer.minima.global/transactions/${TXPOWID}"

jq -n \
    --arg txpowid "$TXPOWID" \
    --arg explorer "$EXPLORER_URL" \
    --arg data "$DATA" \
    --argjson port "$PORT" \
    --arg timestamp "$TIMESTAMP" \
    '{txpowid: $txpowid, explorer: $explorer, data: $data, port: $port, timestamp: $timestamp}'
