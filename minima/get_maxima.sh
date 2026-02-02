#!/bin/bash

RPC_PORT=9005
RPC_URL="http://localhost:$RPC_PORT"

RESPONSE=$(curl -s "${RPC_URL}/maxima%20action:info" 2>/dev/null)

if echo "$RESPONSE" | grep -q '"status":true'; then
    MAXIMA_ADDRESS=$(echo "$RESPONSE" | jq -r '.response.contact' 2>/dev/null)
    if [ -n "$MAXIMA_ADDRESS" ] && [ "$MAXIMA_ADDRESS" != "null" ]; then
        echo "$MAXIMA_ADDRESS"
        exit 0
    fi
fi

echo "Error: Could not retrieve Maxima address. Is the node running?" >&2
exit 1
