#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="$SCRIPT_DIR/cli.sh"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

echo "== MxID: Permanent MAX# Registration =="

TMP="$(mktemp)"
$CLI maxima > "$TMP"

if ! jq -e '.status == true' "$TMP" > /dev/null 2>&1; then
  echo "ERROR: Cannot fetch Maxima info. Is Maxima enabled?"
  exit 1
fi

PUB="$(jq -r '.response.publickey' "$TMP")"
MLS="$(jq -r '.response.mls' "$TMP")"
STATIC="$(jq -r '.response.staticmls' "$TMP")"

if [[ "$STATIC" != "true" ]]; then
  echo "ERROR: Static MLS is not enabled."
  echo "Run: ./mxid_setup_mls.sh"
  exit 1
fi

echo ""
echo "Maxima Public Key:"
echo "$PUB"
echo ""
echo "Static MLS:"
echo "$MLS"
echo ""

echo "Now run THIS on your STATIC MLS NODE (server):"
echo "  maxextra action:addpermanent publickey:$PUB"
echo ""
read -r -p "Press ENTER once done on the MLS node..."

MAXADDR="MAX#$PUB#$MLS"

echo ""
echo "Verifying permanent registration..."
VERIFY="$($CLI maxextra action:getaddress maxaddress:$MAXADDR 2>/dev/null || true)"

if echo "$VERIFY" | jq -e '.status == true' > /dev/null 2>&1; then
  echo "SUCCESS: Permanent MAX# verified!"
else
  echo "WARNING: Could not verify permanent registration."
  echo "The MLS may need time to propagate, or registration may have failed."
fi

echo ""
echo "Permanent MAX# Address:"
echo "$MAXADDR"
