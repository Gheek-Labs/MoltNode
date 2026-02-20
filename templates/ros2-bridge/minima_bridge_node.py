"""
Minima ROS2 Bridge Node (Skeleton)

Publishes Minima node status and wallet balances to ROS2 topics.
This is a reference skeleton — adapt message types to your ROS2 workspace.

Requires:
    - ROS2 (Humble/Iron/Jazzy)
    - minima_client.py from integration/python/

Usage:
    ros2 run minima_bridge minima_bridge_node
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'integration', 'python'))
from minima_client import MinimaClient, MinimaError, MinimaConnectionError

try:
    import rclpy
    from rclpy.node import Node
    HAS_ROS2 = True
except ImportError:
    HAS_ROS2 = False


class MinimaBridgeNode:
    """
    Standalone bridge that can run with or without ROS2.
    With ROS2: publishes to topics.
    Without ROS2: prints to stdout (for testing).
    """

    def __init__(self):
        self.client = MinimaClient(
            host=os.environ.get('MINIMA_HOST', 'localhost'),
            port=int(os.environ.get('MINIMA_PORT', '9005')),
        )

    def get_balance_data(self):
        """
        Fetch and format balance for publishing.

        Returns list of dicts with safe field naming:
        - sendable: available to spend (PRIMARY)
        - confirmed: full balance (includes locked)
        - unconfirmed: pending incoming
        - coins: UTXO count

        supply.total is available but MUST NOT be published as a balance.
        """
        balances = self.client.balance()
        return [
            {
                'token': b['token'],
                'tokenid': b['tokenid'],
                'sendable': float(b['sendable']),
                'confirmed': float(b['confirmed']),
                'unconfirmed': float(b['unconfirmed']),
                'coins': int(b['coins']),
            }
            for b in balances
        ]

    def get_status_data(self):
        """Fetch and format status for publishing."""
        status = self.client.status()
        return {
            'version': status['version'],
            'block': status['block'],
            'chain_height': status['chain_height'],
            'devices': status['devices'],
            'mempool': status['mempool'],
            'timestamp': status['uptime'],
        }

    def get_address_data(self):
        """Fetch receiving address."""
        addr = self.client.getaddress()
        return {
            'address': addr['address'],
            'miniaddress': addr['miniaddress'],
            'publickey': addr['publickey'],
        }


def run_standalone():
    """Run without ROS2 for testing."""
    import time

    bridge = MinimaBridgeNode()
    print("Minima ROS2 Bridge (standalone mode — no ROS2 detected)")
    print(f"Target: {bridge.client.base_url}")
    print()

    while True:
        try:
            status = bridge.get_status_data()
            print(f"[Status] v{status['version']} block={status['block']} devices={status['devices']}")

            balances = bridge.get_balance_data()
            for b in balances:
                print(f"[Balance] {b['token']}: sendable={b['sendable']} confirmed={b['confirmed']} unconfirmed={b['unconfirmed']} coins={b['coins']}")

        except MinimaConnectionError as e:
            print(f"[Error] Connection failed: {e}")
        except MinimaError as e:
            print(f"[Error] RPC error: {e}")

        time.sleep(10)


def main():
    if not HAS_ROS2:
        print("ROS2 not found. Running in standalone mode.")
        run_standalone()
        return

    rclpy.init()

    class ROS2BridgeNode(Node):
        def __init__(self):
            super().__init__('minima_bridge')
            self.bridge = MinimaBridgeNode()
            self.timer = self.create_timer(10.0, self.publish)
            self.get_logger().info('Minima bridge started')

        def publish(self):
            try:
                balances = self.bridge.get_balance_data()
                for b in balances:
                    self.get_logger().info(
                        f"Balance: {b['token']} sendable={b['sendable']} "
                        f"confirmed={b['confirmed']} unconfirmed={b['unconfirmed']}"
                    )

                status = self.bridge.get_status_data()
                self.get_logger().info(
                    f"Status: v{status['version']} block={status['block']}"
                )
            except (MinimaConnectionError, MinimaError) as e:
                self.get_logger().warn(f"Minima error: {e}")

    node = ROS2BridgeNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
