#!/bin/bash
set -euo pipefail

CLI="${CLI:-./minima/cli.sh}"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

echo "== MxID: Static MLS Setup =="

TMP="$(mktemp)"
$CLI maxima > "$TMP"

if ! jq -e '.status == true' "$TMP" > /dev/null 2>&1; then
  echo "ERROR: Cannot fetch Maxima info. Is Maxima enabled?"
  exit 1
fi

STATIC="$(jq -r '.response.staticmls' "$TMP")"
MLS="$(jq -r '.response.mls' "$TMP")"

if [[ "$STATIC" == "true" ]]; then
  echo "Static MLS already set:"
  echo "$MLS"
  exit 0
fi

echo ""
echo "Static MLS is NOT set."
echo "You must provide a server-based Minima P2P identity (Mx...@ip:port) to act as your Static MLS."
echo ""

read -r -p "Enter Static MLS host: " HOST

$CLI maxextra action:staticmls host:"$HOST" | cat

echo ""
echo "Static MLS configured."
