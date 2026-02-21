#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="$SCRIPT_DIR/cli.sh"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

if [[ $# -lt 3 ]]; then
  echo "Usage: $0 <hex_data> <publickey> <signature>"
  echo "Example: $0 0xabc... 0x3081... 0xdeadbeef..."
  exit 1
fi

DATA="$1"
PUB="$2"
SIG="$3"

RESULT="$($CLI maxverify data:"$DATA" publickey:"$PUB" signature:"$SIG")"

if ! echo "$RESULT" | jq -e '.status == true' > /dev/null 2>&1; then
  echo "ERROR: Verification failed."
  echo "$RESULT"
  exit 1
fi

echo "$RESULT" | cat
