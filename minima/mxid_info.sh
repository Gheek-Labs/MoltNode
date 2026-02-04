#!/bin/bash
set -euo pipefail

CLI="${CLI:-./minima/cli.sh}"

command -v jq >/dev/null 2>&1 || { echo "ERROR: jq is required but not installed."; exit 1; }

TMP="$(mktemp)"
$CLI maxima > "$TMP"

if ! jq -e '.status == true' "$TMP" > /dev/null 2>&1; then
  echo "ERROR: Cannot fetch Maxima info. Is Maxima enabled?"
  exit 1
fi

PUB="$(jq -r '.response.publickey' "$TMP")"
MLS="$(jq -r '.response.mls' "$TMP")"
STATIC="$(jq -r '.response.staticmls' "$TMP")"
CONTACT="$(jq -r '.response.contact' "$TMP")"
P2P="$(jq -r '.response.p2pidentity' "$TMP")"
NAME="$(jq -r '.response.name' "$TMP")"

MAXADDR="MAX#${PUB}#${MLS}"

jq -n \
  --arg mxid "MXID:${PUB}" \
  --arg maxima_pubkey "$PUB" \
  --arg maxima_name "$NAME" \
  --arg staticmls "$STATIC" \
  --arg mls "$MLS" \
  --arg maxaddr "$MAXADDR" \
  --arg contact "$CONTACT" \
  --arg p2pidentity "$P2P" \
  '{
    mxid: $mxid,
    maxima_publickey: $maxima_pubkey,
    maxima_name: $maxima_name,
    staticmls: ($staticmls == "true"),
    mls: $mls,
    permanent_max_address: $maxaddr,
    current_contact_address: $contact,
    p2pidentity: $p2pidentity
  }'
