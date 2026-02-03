#!/bin/bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/cli.sh" >/dev/null 2>&1 || true

show_help() {
    cat << 'EOF'
Install a MiniDapp from URL or local file.

Usage:
  ./mds_install.sh <file_or_url> [trust]

Arguments:
  file_or_url   Path to .mds.zip file or URL to download
  trust         Permission level: read (default) or write

Examples:
  ./mds_install.sh /path/to/soko.mds.zip
  ./mds_install.sh https://example.com/soko.mds.zip
  ./mds_install.sh soko.mds.zip write

Output: JSON with installed MiniDapp uid and details
EOF
}

if [[ $# -lt 1 ]] || [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
    show_help
    exit 0
fi

FILE_OR_URL="$1"
TRUST="${2:-read}"

if [[ "$TRUST" != "read" ]] && [[ "$TRUST" != "write" ]]; then
    echo "Error: trust must be 'read' or 'write'" >&2
    exit 1
fi

if [[ "$FILE_OR_URL" =~ ^https?:// ]]; then
    TEMP_DIR=$(mktemp -d)
    FILENAME=$(basename "$FILE_OR_URL")
    DOWNLOAD_PATH="$TEMP_DIR/$FILENAME"
    
    echo "Downloading $FILE_OR_URL..." >&2
    if command -v curl &>/dev/null; then
        curl -sL "$FILE_OR_URL" -o "$DOWNLOAD_PATH"
    elif command -v wget &>/dev/null; then
        wget -q "$FILE_OR_URL" -O "$DOWNLOAD_PATH"
    else
        echo "Error: curl or wget required for URL downloads" >&2
        exit 1
    fi
    
    FILE_PATH="$DOWNLOAD_PATH"
    CLEANUP=true
else
    if [[ ! -f "$FILE_OR_URL" ]]; then
        if [[ -f "$SCRIPT_DIR/$FILE_OR_URL" ]]; then
            FILE_PATH="$SCRIPT_DIR/$FILE_OR_URL"
        else
            echo "Error: File not found: $FILE_OR_URL" >&2
            exit 1
        fi
    else
        FILE_PATH="$(realpath "$FILE_OR_URL")"
    fi
    CLEANUP=false
fi

RESULT=$("$SCRIPT_DIR/cli.sh" mds action:install file:"$FILE_PATH" trust:"$TRUST")

if [[ "$CLEANUP" == "true" ]]; then
    rm -rf "$TEMP_DIR"
fi

echo "$RESULT"
