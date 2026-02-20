# Minima Python Bot

CLI bot that periodically monitors your Minima node's balance and status. Uses the Python integration kit for correct balance display.

## Balance Display (Best Practice)

```
  Token: Minima (0x00...)
    Sendable:                 1000  <- spendable now
    Confirmed:                1000  <- full balance (includes locked)
    Unconfirmed:                 0  <- pending
    Coins:                       3  <- UTXO count
```

**Never display `supply.total` as a balance** — it's the token hardcap (~1B for Minima).

## Setup

```bash
cd templates/python-bot
python bot.py
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MINIMA_HOST` | `localhost` | Minima node host |
| `MINIMA_PORT` | `9005` | RPC port |
| `INTERVAL` | `60` | Seconds between checks |
| `ALERT_THRESHOLD` | `0` | Alert when sendable drops below this (0 = disabled) |

## Example: Alert on Low Balance

```bash
INTERVAL=30 ALERT_THRESHOLD=100 python bot.py
```

## Architecture

```
bot.py    # Periodic monitor using ../../integration/python/minima_client.py
```

Uses `MinimaClient.balance()` which returns normalized objects with `total` hidden under `supply.total`.
