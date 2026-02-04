#!/bin/bash
set -euo pipefail

CLI="${CLI:-./minima/cli.sh}"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <hex_data>"
  echo "Example: $0 0xabc123..."
  exit 1
fi

DATA="$1"

RESULT="$($CLI maxsign data:"$DATA")"

if ! echo "$RESULT" | jq -e '.status == true' > /dev/null 2>&1; then
  echo "ERROR: Failed to sign data."
  echo "$RESULT"
  exit 1
fi

echo "$RESULT" | cat
