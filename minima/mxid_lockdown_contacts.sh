#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="$SCRIPT_DIR/cli.sh"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

echo "== MxID: Contact Lockdown =="

RESULT="$($CLI maxextra action:allowallcontacts enable:false)"

if ! echo "$RESULT" | jq -e '.status == true' > /dev/null 2>&1; then
  echo "ERROR: Failed to lock down contacts."
  exit 1
fi

echo ""
echo "Contact requests now rejected by default."
echo "To whitelist a trusted contact pubkey:"
echo "  $CLI maxextra action:addallowed publickey:<PUBKEY>"
