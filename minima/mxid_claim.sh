#!/bin/bash
set -euo pipefail

CLI="${CLI:-./minima/cli.sh}"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

echo "== MxID: Claim Identity =="

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
  echo "MxID incomplete: Static MLS not enabled."
  echo "Run: ./mxid_setup_mls.sh"
  exit 1
fi

MAXADDR="MAX#$PUB#$MLS"

echo ""
echo "Verifying permanent MAX# registration..."
VERIFY="$($CLI maxextra action:getaddress maxaddress:$MAXADDR 2>/dev/null || true)"

if ! echo "$VERIFY" | jq -e '.status == true' > /dev/null 2>&1; then
  echo "WARNING: Permanent MAX# could not be verified."
  echo "Run mxid_register_permanent.sh to complete registration."
  echo ""
  read -r -p "Continue anyway? (y/N): " CONTINUE
  if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
    exit 1
  fi
fi

echo ""
echo "MxID (Root):"
echo "MXID:$PUB"
echo ""
echo "Public Reachability (Permanent MAX# format):"
echo "$MAXADDR"
echo ""
echo "MxID claimed (cryptographic root + stable routing)."
