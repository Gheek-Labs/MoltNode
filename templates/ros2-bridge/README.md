# Minima ROS2 Bridge

Skeleton for bridging Minima RPC into ROS2 topics. Publishes node status and wallet balances as ROS2 messages.

## Message Mapping

### MinimaBalance.msg
```
string token
string tokenid
float64 sendable       # Available to spend — PRIMARY BALANCE
float64 confirmed      # Full wallet balance (includes locked)
float64 unconfirmed    # Pending incoming
int32 coins            # Number of UTXOs
# NOTE: 'total' (token hardcap) is intentionally excluded
```

### MinimaStatus.msg
```
string version
int64 block
int64 chain_height
int32 devices
int32 mempool
string timestamp
```

### MinimaAddress.msg
```
string address         # 0x-prefixed hex address
string miniaddress     # MxG-prefixed human address
string publickey       # Associated public key
```

## Architecture

```
ros2_bridge/
  minima_bridge_node.py    # ROS2 node (publisher)
  msg/
    MinimaBalance.msg
    MinimaStatus.msg
    MinimaAddress.msg
  launch/
    bridge.launch.py       # Launch file
  package.xml
  setup.py
```

## Setup

1. Place in your ROS2 workspace `src/` directory
2. Copy `../../integration/python/minima_client.py` into the package
3. Build: `colcon build --packages-select minima_bridge`
4. Run: `ros2 run minima_bridge minima_bridge_node`

## Topics Published

| Topic | Type | Rate |
|-------|------|------|
| `/minima/balance` | `MinimaBalance[]` | 0.1 Hz |
| `/minima/status` | `MinimaStatus` | 0.1 Hz |
| `/minima/address` | `MinimaAddress` | On startup |

## Example Node (Skeleton)

```python
import rclpy
from rclpy.node import Node
from minima_client import MinimaClient

class MinimaBridgeNode(Node):
    def __init__(self):
        super().__init__('minima_bridge')
        self.client = MinimaClient()
        self.timer = self.create_timer(10.0, self.publish_balance)

    def publish_balance(self):
        balances = self.client.balance()
        for b in balances:
            # Use sendable as primary balance
            self.get_logger().info(
                f"{b['token']}: sendable={b['sendable']} "
                f"confirmed={b['confirmed']} "
                f"unconfirmed={b['unconfirmed']}"
            )
            # supply.total is the hardcap — NEVER publish as balance

def main():
    rclpy.init()
    node = MinimaBridgeNode()
    rclpy.spin(node)
    rclpy.shutdown()
```

## Balance Display Warning

The Minima RPC `balance` response contains a `total` field that is the **token maximum supply** (~1 billion for Minima), **NOT** the wallet balance. The integration kit moves this to `supply.total` to prevent accidental misuse.

When mapping to ROS2 messages:
- Publish `sendable` as the primary balance
- Publish `confirmed` as full balance
- Publish `unconfirmed` as pending
- **Do NOT** publish `total` / `supply.total` as any kind of balance
