#!/bin/bash
set -euo pipefail

CLI="${CLI:-./minima/cli.sh}"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

extract_hex_0x() {
  jq -r '
    (
      .. | .hex? // .random? // .data? // .result? // empty
    ) as $v
    | if ($v|type) == "string" and ($v|test("^0x[0-9a-fA-F]+$")) then $v else empty end
    ' 2>/dev/null
}

scan_hex_0x() {
  grep -Eo '0x[0-9a-fA-F]+' | head -n 1 || true
}

need_64_hex_chars() {
  local hex_no_prefix="$1"
  hex_no_prefix="$(echo "$hex_no_prefix" | tr -cd '0-9a-fA-F')"
  local len="${#hex_no_prefix}"

  if (( len >= 64 )); then
    echo "0x${hex_no_prefix:0:64}"
    return 0
  fi

  echo ""
  return 0
}

for _ in {1..8}; do
  OUT="$("$CLI" random)"
  HEX="$(echo "$OUT" | extract_hex_0x || true)"

  if [[ -z "$HEX" ]]; then
    HEX="$(echo "$OUT" | scan_hex_0x || true)"
  fi

  if [[ -n "$HEX" ]]; then
    CHAL="$(need_64_hex_chars "${HEX#0x}")"
    if [[ -n "$CHAL" ]]; then
      echo "$CHAL"
      exit 0
    fi
  fi
done

echo "ERROR: Failed to generate a 32-byte challenge from Minima RANDOM output."
echo "Raw last output:"
echo "$OUT"
exit 1
