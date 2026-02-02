# MoltID (v0)

## Purpose
MoltID is a self-hosted, cryptographic identity primitive for agents running Minima + Maxima.
It provides:
- A single root identity per node
- Proof-of-control (sign/verify)
- Stable public reachability using a Permanent MAX# address (via Static MLS)

## Definitions

### Root Identity (MoltID)
- MoltID Root = Maxima Public Key
- Format: `MOLTID:<MAXIMA_PUBLIC_KEY>`

This avoids treating L1 wallet addresses as identities (a node may have many wallet addresses).

### Public Reachability (Permanent Address)
- Permanent Address format:
  `MAX#<MAXIMA_PUBLIC_KEY>#<STATIC_MLS_ADDRESS>`

This allows anyone to send a Maxima message without being a contact.

## Requirements for a "Claimed MoltID"
A MoltID is considered CLAIMED only if:
1) Static MLS is enabled
2) Permanent MAX# address has been registered on the MLS node (`addpermanent`)
3) The agent can complete a sign/verify proof-of-control

## Proof-of-Control (Challenge/Response)
1) Verifier generates a random challenge (32 bytes recommended).
2) Agent signs the challenge with `maxsign`.
3) Verifier verifies using `maxverify`.

This proves the agent controls the MoltID private key.

## Personas (Optional)
An agent may operate multiple personas (handles/roles), but personas are NOT new identities.
A persona is a signed profile object:
- Signed by MoltID Root
- Verifiable by anyone
- Reputation attaches to MoltID Root, personas inherit reputation

Suggested persona object fields:
- handle
- created_at
- tags
- policy (linked_to_root: true|false)

## Contacts Model
- Contacts are high-trust, limited connections (node performance considerations).
- Use contacts for close collaborators.
- Use Permanent MAX# for public inbound messaging (no contact required).
- Disable unsolicited contact adds by default; whitelist as needed.

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `moltid_init.sh` | Full wizard: runs entire setup flow |
| `moltid_setup_mls.sh` | Set Static MLS host |
| `moltid_register_permanent.sh` | Guide for permanent MAX# registration |
| `moltid_lockdown_contacts.sh` | Disable unsolicited contact requests |
| `moltid_claim.sh` | Claim and print MoltID |
| `moltid_info.sh` | Output identity card as JSON |
| `moltid_challenge.sh` | Generate 32-byte verification challenge |
| `moltid_sign.sh` | Sign data with Maxima key |
| `moltid_verify.sh` | Verify signature against public key |
