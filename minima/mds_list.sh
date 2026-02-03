#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat << 'EOF'
List installed MiniDapps with their session IDs.

Usage:
  ./mds_list.sh [options]

Options:
  --json    Output raw JSON (default)
  --table   Output as formatted table
  --uid     Output only UIDs (one per line)

Output fields:
  uid         Unique identifier for the MiniDapp
  name        Display name
  version     Version string
  trust       Permission level (read/write)
  sessionid   Session ID for API access

Examples:
  ./mds_list.sh
  ./mds_list.sh --table
  ./mds_list.sh --uid
EOF
}

FORMAT="json"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -h|--help)
            show_help
            exit 0
            ;;
        --json)
            FORMAT="json"
            shift
            ;;
        --table)
            FORMAT="table"
            shift
            ;;
        --uid)
            FORMAT="uid"
            shift
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

RESULT=$("$SCRIPT_DIR/cli.sh" mds action:list)

case "$FORMAT" in
    json)
        echo "$RESULT"
        ;;
    table)
        if ! command -v jq &>/dev/null; then
            echo "Error: jq required for table output" >&2
            exit 1
        fi
        printf "%-64s %-20s %-10s %s\n" "UID" "NAME" "VERSION" "TRUST"
        printf "%-64s %-20s %-10s %s\n" "$(printf '%.0s-' {1..64})" "$(printf '%.0s-' {1..20})" "$(printf '%.0s-' {1..10})" "-----"
        echo "$RESULT" | jq -r '.response.minidapps[] | [.uid, (.conf.name // "unknown"), (.conf.version // "?"), (.trust // "null")] | @tsv' | \
            while IFS=$'\t' read -r uid name version trust; do
                printf "%-64s %-20s %-10s %s\n" "$uid" "${name:0:20}" "${version:0:10}" "$trust"
            done
        ;;
    uid)
        if ! command -v jq &>/dev/null; then
            echo "Error: jq required for uid output" >&2
            exit 1
        fi
        echo "$RESULT" | jq -r '.response.minidapps[].uid'
        ;;
esac
