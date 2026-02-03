#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    cat << 'EOF'
Send API requests to an installed MiniDapp via MDS.

Usage:
  ./mds_api.sh <minidapp_name_or_uid> <endpoint> [data]

Arguments:
  minidapp    Name (partial match) or UID of the MiniDapp
  endpoint    API endpoint path (e.g., /api/orders, /service.js)
  data        Optional JSON data for POST requests

Environment:
  MDS_PASSWORD   Required - MDS authentication password

Examples:
  ./mds_api.sh soko /api/list
  ./mds_api.sh soko /service.js '{"action":"getorders"}'
  ./mds_api.sh 0xABC123 /api/buy '{"nft":"0x..."}'

Notes:
  - MDS runs on port 9003 with SSL
  - Each MiniDapp has a unique session ID for API access
  - Use mds_list.sh to find MiniDapp UIDs and session IDs
EOF
}

if [[ $# -lt 2 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_help
    exit 0
fi

MINIDAPP="$1"
ENDPOINT="$2"
DATA="${3:-}"

MDS_PORT="${MDS_PORT:-9003}"

if [[ -z "${MDS_PASSWORD:-}" ]]; then
    echo "Error: MDS_PASSWORD environment variable required" >&2
    exit 1
fi

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required" >&2
    exit 1
fi

LIST_RESULT=$("$SCRIPT_DIR/cli.sh" mds action:list)

if [[ "$MINIDAPP" == 0x* ]]; then
    MINIDAPP_INFO=$(echo "$LIST_RESULT" | jq -r --arg uid "$MINIDAPP" '.response.minidapps[] | select(.uid == $uid)')
else
    MINIDAPP_INFO=$(echo "$LIST_RESULT" | jq -r --arg name "$MINIDAPP" '.response.minidapps[] | select(.conf.name | ascii_downcase | contains($name | ascii_downcase))')
fi

if [[ -z "$MINIDAPP_INFO" ]] || [[ "$MINIDAPP_INFO" == "null" ]]; then
    echo "Error: MiniDapp not found: $MINIDAPP" >&2
    echo "Installed MiniDapps:" >&2
    echo "$LIST_RESULT" | jq -r '.response.minidapps[] | "  \(.conf.name // "unknown") (\(.uid))"' >&2
    exit 1
fi

SESSION_ID=$(echo "$MINIDAPP_INFO" | jq -r '.sessionid')
MINIDAPP_UID=$(echo "$MINIDAPP_INFO" | jq -r '.uid')
MINIDAPP_NAME=$(echo "$MINIDAPP_INFO" | jq -r '.conf.name // "unknown"')

ENDPOINT="${ENDPOINT#/}"

URL="https://127.0.0.1:${MDS_PORT}/${SESSION_ID}/${ENDPOINT}"

echo "Calling $MINIDAPP_NAME ($MINIDAPP_UID)" >&2
echo "URL: $URL" >&2

if [[ -n "$DATA" ]]; then
    RESPONSE=$(curl -sk -X POST \
        -H "Content-Type: application/json" \
        -u "minima:${MDS_PASSWORD}" \
        -d "$DATA" \
        "$URL")
else
    RESPONSE=$(curl -sk \
        -u "minima:${MDS_PASSWORD}" \
        "$URL")
fi

echo "$RESPONSE"
