#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CLI="$SCRIPT_DIR/cli.sh"
AUTO_LOCKDOWN="${AUTO_LOCKDOWN:-true}"

P2P_PORT="${P2P_PORT:-9001}"
COMMUNITY_MLS_HOST="${COMMUNITY_MLS_HOST:-}"
AUTO_DETECT_MLS="${AUTO_DETECT_MLS:-true}"
PREFER_SOVEREIGN_MLS="${PREFER_SOVEREIGN_MLS:-true}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "ERROR: Missing required command: $1"
    exit 1
  }
}

tmpjson() {
  mktemp 2>/dev/null || mktemp -t mxid
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
  "$SCRIPT_DIR/mxid_challenge.sh"
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

print_graduate_command() {
  local cli="$1"
  echo ""
  echo "------------------------------------------------------------"
  echo "Upgrade to TRUE SOVEREIGNTY later (run on a SERVER instance):"
  echo "------------------------------------------------------------"
  echo "${cli} maxextra action:staticmls host:\$(${cli} maxima | jq -r '.response.p2pidentity')"
  echo ""
  echo "After switching to self-MLS, re-register your Permanent MAX# on the new MLS:"
  echo "  (run on the MLS node)  maxextra action:addpermanent publickey:<your-primary-publickey>"
  echo ""
}

pause() {
  echo ""
  read -r -p "Press ENTER to continue..."
}

is_valid_ipv4() {
  local ip="$1"
  [[ "$ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]
}

is_private_ip() {
  local ip="$1"
  if ! is_valid_ipv4 "$ip"; then
    return 0
  fi
  [[ "$ip" =~ ^10\. ]] && return 0
  [[ "$ip" =~ ^127\. ]] && return 0
  [[ "$ip" =~ ^192\.168\. ]] && return 0
  [[ "$ip" =~ ^169\.254\. ]] && return 0
  [[ "$ip" =~ ^0\. ]] && return 0
  if [[ "$ip" =~ ^172\.([0-9]+)\. ]]; then
    local b="${BASH_REMATCH[1]}"
    (( b >= 16 && b <= 31 )) && return 0
  fi
  if [[ "$ip" =~ ^100\.([0-9]+)\. ]]; then
    local b="${BASH_REMATCH[1]}"
    (( b >= 64 && b <= 127 )) && return 0
  fi
  [[ "$ip" =~ ^22[4-9]\. ]] && return 0
  [[ "$ip" =~ ^23[0-9]\. ]] && return 0
  [[ "$ip" =~ ^24[0-9]\. ]] && return 0
  [[ "$ip" =~ ^25[0-5]\. ]] && return 0
  return 1
}

extract_ip_from_p2pidentity() {
  local ident="$1"
  echo "$ident" | sed -nE 's/.*@([^:]+):([0-9]+).*/\1/p'
}

extract_port_from_p2pidentity() {
  local ident="$1"
  echo "$ident" | sed -nE 's/.*@([^:]+):([0-9]+).*/\2/p'
}

is_listening_on_port() {
  local port="$1"
  if command -v ss >/dev/null 2>&1; then
    ss -ltn 2>/dev/null | grep -qE ":$port\s"
    return $?
  elif command -v netstat >/dev/null 2>&1; then
    netstat -ltn 2>/dev/null | grep -qE ":$port\s"
    return $?
  else
    return 2
  fi
}

banner "MxID Init Wizard"
echo "CLI: $CLI"

[[ -x "$CLI" ]] || {
  echo "ERROR: Cannot execute CLI at: $CLI"
  echo "   Set CLI env var or ensure ./minima/cli.sh exists and is executable."
  exit 1
}

need_cmd jq

banner "Step 1/7: Read Maxima Info"
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

banner "Step 2/7: Set Maxima Name (Nickname)"
echo "Your current Maxima name is: $NAME"
echo ""
echo "NOTE: maxima_name is just a nickname - it is NOT unique and NOT verified."
echo "      Your MxID (Maxima public key) is your true unique identity."
echo "      The name is for human readability only."
echo ""
if [[ "$NAME" == "noname" || -z "$NAME" ]]; then
  read -r -p "Enter a display name for your node (or press ENTER to skip): " NEW_NAME
else
  read -r -p "Change name? (press ENTER to keep '$NAME', or type new name): " NEW_NAME
fi

if [[ -n "$NEW_NAME" ]]; then
  run_cli maxima action:setname name:"$NEW_NAME"
  NAME="$NEW_NAME"
  echo ""
  echo "Maxima name set to: $NAME"
else
  echo "Keeping current name: $NAME"
fi

banner "Step 3/7: Ensure Static MLS"

if [[ "$STATIC" == "true" ]]; then
  echo "Static MLS already enabled."
else
  echo "Static MLS is NOT enabled."
  echo ""

  MLS_MODE=""
  REASON=""

  if [[ "$AUTO_DETECT_MLS" == "true" ]]; then
    IP="$(extract_ip_from_p2pidentity "$P2P")"
    PORT_DETECTED="$(extract_port_from_p2pidentity "$P2P")"
    [[ -n "$PORT_DETECTED" ]] && P2P_PORT="$PORT_DETECTED"

    if [[ -z "$IP" ]]; then
      REASON="Could not parse IP from p2pidentity."
      MLS_MODE="manual"
    elif is_private_ip "$IP"; then
      REASON="p2pidentity uses private/reserved IP ($IP) - not suitable as Static MLS host."
      if [[ -n "$COMMUNITY_MLS_HOST" ]]; then
        MLS_MODE="community"
      else
        MLS_MODE="manual"
      fi
    else
      LISTEN_STATUS=0
      PORT_CHECK_UNAVAILABLE=false
      if is_listening_on_port "$P2P_PORT"; then
        REASON="Public IP ($IP) and port $P2P_PORT appears to be listening."
        LISTEN_STATUS=0
      else
        LISTEN_STATUS=$?
        if [[ "$LISTEN_STATUS" -eq 1 ]]; then
          REASON="Public IP ($IP) but port $P2P_PORT does not appear to be listening locally."
        else
          REASON="Public IP ($IP); cannot confirm listening port (ss/netstat unavailable). Assuming sovereign."
          PORT_CHECK_UNAVAILABLE=true
        fi
      fi

      if [[ "$PREFER_SOVEREIGN_MLS" == "true" && ( "$LISTEN_STATUS" -eq 0 || "$PORT_CHECK_UNAVAILABLE" == "true" ) ]]; then
        MLS_MODE="self"
      elif [[ -n "$COMMUNITY_MLS_HOST" ]]; then
        MLS_MODE="community"
      else
        MLS_MODE="manual"
      fi
    fi

    echo "Auto-detect result: $REASON"
    echo ""
  else
    MLS_MODE="manual"
  fi

  if [[ "$MLS_MODE" == "self" ]]; then
    echo "Selecting SOVEREIGN route: this node will act as its own Static MLS."
    echo "Using host (this node p2pidentity):"
    echo "  $P2P"
    HOST="$P2P"

  elif [[ "$MLS_MODE" == "community" ]]; then
    echo "Selecting COMMUNITY MLS route (recommended for non-server environments)."
    echo "Using community MLS host:"
    echo "  $COMMUNITY_MLS_HOST"
    echo ""
    echo "You can upgrade to full sovereignty later by running your own MLS server."
    HOST="$COMMUNITY_MLS_HOST"

    print_graduate_command "$CLI"

  else
    echo "Manual selection required."
    if [[ -n "$COMMUNITY_MLS_HOST" ]]; then
      echo "Press ENTER to use community MLS, or paste your own server p2pidentity:"
      echo "  $COMMUNITY_MLS_HOST"
      read -r -p "Enter Static MLS host P2P identity: " HOST
      [[ -z "$HOST" ]] && HOST="$COMMUNITY_MLS_HOST"
    else
      echo "Paste your server p2pidentity in this format: Mx...@ip:port"
      read -r -p "Enter Static MLS host P2P identity: " HOST
      [[ -z "$HOST" ]] && { echo "ERROR: No host provided."; exit 1; }
    fi
  fi

  run_cli maxextra action:staticmls host:"$HOST"

  MAXF="$(fetch_maxima)"
  STATIC="$(get_field "$MAXF" '.response.staticmls')"
  MLS="$(get_field "$MAXF" '.response.mls')"

  if [[ "$STATIC" != "true" ]]; then
    echo "ERROR: Failed to enable Static MLS."
    exit 1
  fi
  echo ""
  echo "Static MLS enabled. MLS:"
  echo "  $MLS"
fi

MAXADDR="MAX#${PUB}#${MLS}"

banner "Step 4/7: Register Permanent MAX# Address"
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

banner "Step 5/7: Contact Lockdown (Recommended)"
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

banner "Step 6/7: Claim MxID (Root Identity)"
echo "MxID Root:"
echo "  MXID:$PUB"
echo ""
echo "Permanent Reachability:"
echo "  $MAXADDR"
echo ""
echo "Identity Card (JSON):"
jq -n \
  --arg mxid "MXID:${PUB}" \
  --arg maxima_pubkey "$PUB" \
  --arg maxima_name "$NAME" \
  --arg mls "$MLS" \
  --arg maxaddr "$MAXADDR" \
  --arg contact "$CONTACT" \
  --arg p2pidentity "$P2P" \
  --arg staticmls "$STATIC" \
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

banner "Step 7/7: Ready-to-Post Moltbook Snippet"
echo "Copy/paste this to Moltbook:"
cat <<EOF

MxID Verified (self-hosted)
MxID: MXID:$PUB
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
echo "MxID init complete."
echo "Remember: Permanent MAX# requires the addpermanent step on your Static MLS node."
