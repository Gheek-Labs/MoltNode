# Agent Quickstart

Quick reference for programmatic Minima node operations.

**Full command reference:** See [COMMANDS.md](COMMANDS.md)

---

## 1. Run Node

```bash
./minima/start.sh
```

Or use the configured workflow (auto-starts).

**Verify running:**
```bash
./minima/cli.sh status
```

---

## 2. Get Maxima Address

```bash
./minima/get_maxima.sh
```

**Python:**
```python
import subprocess
addr = subprocess.check_output(["./minima/get_maxima.sh"]).decode().strip()
```

**Note:** Address rotates every few minutes - always fetch fresh.

---

## 3. Send Value

```bash
./minima/cli.sh send address:MxG... amount:1
```

**With token:**
```bash
./minima/cli.sh send address:MxG... amount:10 tokenid:0x...
```

**Check balance first:**
```bash
./minima/cli.sh balance
```

---

## 4. Add Maxima Contact

```bash
./minima/cli.sh maxcontacts action:add contact:MxG...@IP:PORT
```

**List contacts:**
```bash
./minima/cli.sh maxcontacts action:list
```

**Remove contact:**
```bash
./minima/cli.sh maxcontacts action:remove id:0
```

**Search contact by publickey:**
```bash
./minima/cli.sh maxcontacts action:search publickey:0x3081..
```

---

## 5. Send Maxima Message

**Send by contact address:**
```bash
./minima/cli.sh maxima action:send to:MxG... application:myapp data:0xFED5..
```

**Send by contact ID:**
```bash
./minima/cli.sh maxima action:send id:0 application:myapp data:0xFED5..
```

**Send by publickey with polling (retries until success):**
```bash
./minima/cli.sh maxima action:send publickey:0xCD34.. application:myapp data:0xFED5.. poll:true
```

**Broadcast to ALL contacts:**
```bash
./minima/cli.sh maxima action:sendall application:myapp data:0xFED5..
```

**Set your display name:**
```bash
./minima/cli.sh maxima action:setname name:MyAgentNode
```

**Refresh contacts (re-sync):**
```bash
./minima/cli.sh maxima action:refresh
```

---

## 6. Sign & Verify Messages

**Sign data with your Maxima ID:**
```bash
./minima/cli.sh maxsign data:0xCD34..
```

**Verify signature:**
```bash
./minima/cli.sh maxverify data:0xCD34.. publickey:0xFED5.. signature:0x4827..
```

**Create RSA keypair for custom signing:**
```bash
./minima/cli.sh maxcreate
```

---

## 7. Advanced: Permanent Maxima Address

For static/always-reachable addresses (useful for bots/servers):

**Set static MLS host:**
```bash
./minima/cli.sh maxextra action:staticmls host:Mx...@34.190.784.3:9001
```

**Register for public contact lookup:**
```bash
./minima/cli.sh maxextra action:addpermanent publickey:0x3081..
```

**Get someone's current address from their MLS:**
```bash
./minima/cli.sh maxextra action:getaddress maxaddress:MAX#0x3081..#Mx..@34.190.784.3:9001
```

**Control who can add you as contact:**
```bash
./minima/cli.sh maxextra action:allowallcontacts enable:false
./minima/cli.sh maxextra action:addallowed publickey:0x2451..
```

---

## RPC Endpoint

All commands available via HTTP:

```
http://localhost:9005/<command>
```

**Example:**
```bash
curl "http://localhost:9005/status"
curl "http://localhost:9005/balance"
curl "http://localhost:9005/maxima%20action:info"
```

---

## Python Agent Example

```python
import requests
import subprocess

RPC = "http://localhost:9005"

def cmd(c):
    return requests.get(f"{RPC}/{c}").json()

def get_maxima_address():
    return subprocess.check_output(["./minima/get_maxima.sh"]).decode().strip()

# Get node status
status = cmd("status")

# Get my Maxima address
my_addr = get_maxima_address()

# Check balance
balance = cmd("balance")

# Add a contact
cmd("maxcontacts action:add contact:MxG...@1.2.3.4:9001")

# Send message
cmd("maxima action:send id:0 application:agent data:ping")

# Send value
cmd("send address:MxG... amount:1")
```
