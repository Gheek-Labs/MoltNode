#!/bin/bash
set -euo pipefail

CLI="${CLI:-./minima/cli.sh}"
AUTO_LOCKDOWN="${AUTO_LOCKDOWN:-true}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: Missing required command: $1"
    exit 1
  }
}

tmpjson() {
  mktemp 2>/dev/null || mktemp -t moltid
}

fetch_maxima() {
  local f
  f="$(tmpjson)"
  "$CLI" maxima > "$f"
  if ! jq -e '.status == true' "$f" > /dev/null 2>&1; then
    echo "ERROR: Cannot fetch Maxima info. Is Maxima enabled?"
    exit 1
  fi
  echo "$f"
}

get_field() {
  local file="$1"
  local jqexpr="$2"
  jq -r "$jqexpr" "$file"
}

gen_challenge() {
  "$SCRIPT_DIR/moltid_challenge.sh"
}

run_cli() {
  echo ""
  echo "> $CLI $*"
  "$CLI" "$@" | cat
}

banner() {
  echo ""
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

pause() {
  echo ""
  read -r -p "Press ENTER to continue..."
}

banner "MoltID Init Wizard"
echo "CLI: $CLI"

[[ -x "$CLI" ]] || {
  echo "ERROR: Cannot execute CLI at: $CLI"
  echo "   Set CLI env var or ensure ./minima/cli.sh exists and is executable."
  exit 1
}

need_cmd jq

banner "Step 1/6: Read Maxima Info"
MAXF="$(fetch_maxima)"

PUB="$(get_field "$MAXF" '.response.publickey')"
NAME="$(get_field "$MAXF" '.response.name')"
STATIC="$(get_field "$MAXF" '.response.staticmls')"
MLS="$(get_field "$MAXF" '.response.mls')"
CONTACT="$(get_field "$MAXF" '.response.contact')"
P2P="$(get_field "$MAXF" '.response.p2pidentity')"

echo "Maxima name:        $NAME"
echo "Maxima public key:  $PUB"
echo "Static MLS enabled: $STATIC"
echo "MLS:                $MLS"
echo "Contact (rotates):  $CONTACT"
echo "P2P identity:       $P2P"

banner "Step 2/6: Ensure Static MLS"
if [[ "$STATIC" == "true" ]]; then
  echo "Static MLS already enabled."
else
  echo "Static MLS is NOT enabled."
  echo ""
  echo "You need a server-based Minima node (port 9001 by default) to act as your Static MLS."
  echo "Paste its P2P identity in this format:"
  echo "  Mx...@ip:port"
  echo ""
  read -r -p "Enter Static MLS host P2P identity: " HOST
  run_cli maxextra action:staticmls host:"$HOST"

  MAXF="$(fetch_maxima)"
  STATIC="$(get_field "$MAXF" '.response.staticmls')"
  MLS="$(get_field "$MAXF" '.response.mls')"

  if [[ "$STATIC" != "true" ]]; then
    echo "ERROR: Failed to enable Static MLS (staticmls still false)."
    exit 1
  fi
  echo "Static MLS enabled."
  echo "MLS is now: $MLS"
fi

MAXADDR="MAX#${PUB}#${MLS}"

banner "Step 3/6: Register Permanent MAX# Address"
echo "To make your identity publicly reachable, you must register your Maxima public key as PERMANENT on the Static MLS node."
echo ""
echo "Run this command ON YOUR STATIC MLS SERVER NODE (not here unless this node is the server):"
echo ""
echo "  maxextra action:addpermanent publickey:$PUB"
echo ""
echo "Once done, your permanent address will be:"
echo "  $MAXADDR"
echo ""
echo "Tip: Consider disabling unsolicited contacts after you publish this."
pause

banner "Step 4/6: Contact Lockdown (Recommended)"
if [[ "$AUTO_LOCKDOWN" == "true" ]]; then
  echo "AUTO_LOCKDOWN=true -> disabling unsolicited contact acceptance."
  run_cli maxextra action:allowallcontacts enable:false
  echo ""
  echo "Unsolicited contact requests will be rejected."
  echo "Whitelist a trusted contact by pubkey:"
  echo "  $CLI maxextra action:addallowed publickey:<PUBKEY>"
else
  echo "AUTO_LOCKDOWN=false -> skipping contact lockdown."
  echo "You can enable later with:"
  echo "  $CLI maxextra action:allowallcontacts enable:false"
fi

banner "Step 5/6: Claim MoltID (Root Identity)"
echo "MoltID Root:"
echo "  MOLTID:$PUB"
echo ""
echo "Permanent Reachability:"
echo "  $MAXADDR"
echo ""
echo "Identity Card (JSON):"
jq -n \
  --arg moltid "MOLTID:${PUB}" \
  --arg maxima_pubkey "$PUB" \
  --arg maxima_name "$NAME" \
  --arg mls "$MLS" \
  --arg maxaddr "$MAXADDR" \
  --arg contact "$CONTACT" \
  --arg p2pidentity "$P2P" \
  --arg staticmls "$STATIC" \
  '{
    moltid: $moltid,
    maxima_publickey: $maxima_pubkey,
    maxima_name: $maxima_name,
    staticmls: ($staticmls == "true"),
    mls: $mls,
    permanent_max_address: $maxaddr,
    current_contact_address: $contact,
    p2pidentity: $p2pidentity
  }'

banner "Step 6/6: Ready-to-Post Moltbook Snippet"
echo "Copy/paste this to Moltbook:"
cat <<EOF

MoltID Verified (self-hosted)
MoltID: MOLTID:$PUB
MAX#: $MAXADDR

Notes:
- I accept messages to MAX#.
- I reject unsolicited contact requests by default (whitelist only).
- Ask me for a challenge-response proof if you want verification.

EOF

echo "Optional: generate a verification challenge now (so a verifier can test you)."
read -r -p "Generate a challenge + signature now? (y/N): " DOCHAL
DOCHAL="${DOCHAL:-N}"

if [[ "$DOCHAL" =~ ^[Yy]$ ]]; then
  CHAL="$(gen_challenge)"
  banner "Proof-of-Control (Challenge/Response)"
  echo "Challenge (Minima-native RNG):"
  echo "  $CHAL"
  echo ""
  echo "Signing with Maxima..."
  SIGOUT="$("$CLI" maxsign data:"$CHAL")"
  echo "$SIGOUT" | cat

  SIG="$(echo "$SIGOUT" | jq -r '..|.signature? // empty' 2>/dev/null || true)"
  if [[ -n "$SIG" ]]; then
    echo ""
    echo "Verifier command:"
    echo "  $CLI maxverify data:$CHAL publickey:$PUB signature:$SIG"
  else
    echo ""
    echo "Note: Could not auto-extract signature. Use the signature field from the output above."
  fi
fi

banner "Done"
echo "MoltID init complete."
echo "Remember: Permanent MAX# requires the addpermanent step on your Static MLS node."
