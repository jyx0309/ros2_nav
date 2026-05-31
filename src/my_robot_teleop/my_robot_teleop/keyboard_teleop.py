import sys
import select
import termios
import time
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


HELP_TEXT = """
Keyboard teleop started.
------------------------
w: forward
s: backward
a: turn left
d: turn right
x: stop
q: quit
"""


class KeyboardTeleop(Node):
    def __init__(self):
        super().__init__('keyboard_teleop')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_x = 0.0
        self.angular_z = 0.0

        self.linear_step = 0.05
        self.angular_step = 0.15

        self.max_linear = 0.25
        self.max_angular = 0.7

        self.get_logger().info(HELP_TEXT)

    def publish_cmd(self):
        msg = Twist()
        msg.linear.x = self.linear_x
        msg.angular.z = self.angular_z
        self.cmd_pub.publish(msg)

    def stop(self):
        self.linear_x = 0.0
        self.angular_z = 0.0
        self.publish_cmd()

    def ramp_stop(self, steps=10, delay=0.03):
        start_linear = self.linear_x
        start_angular = self.angular_z

        for step in range(steps - 1, -1, -1):
            scale = step / steps
            self.linear_x = start_linear * scale
            self.angular_z = start_angular * scale
            self.publish_cmd()
            time.sleep(delay)

    def handle_key(self, key):
        if key == 'w':
            self.linear_x = min(self.linear_x + self.linear_step, self.max_linear)
        elif key == 's':
            self.linear_x = max(self.linear_x - self.linear_step, -self.max_linear)
        elif key == 'a':
            self.angular_z = min(self.angular_z + self.angular_step, self.max_angular)
        elif key == 'd':
            self.angular_z = max(self.angular_z - self.angular_step, -self.max_angular)
        elif key == 'x':
            self.ramp_stop()
        elif key == 'q':
            self.ramp_stop()
            return False

        self.publish_cmd()
        self.get_logger().info(
            f'linear.x={self.linear_x:.2f}, angular.z={self.angular_z:.2f}'
        )
        return True


def get_key(timeout=0.1):
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.read(1)
    return None


def main(args=None):
    rclpy.init(args=args)
    node = KeyboardTeleop()

    old_settings = termios.tcgetattr(sys.stdin)

    try:
        tty.setcbreak(sys.stdin.fileno())

        running = True
        while rclpy.ok() and running:
            rclpy.spin_once(node, timeout_sec=0.01)

            key = get_key(timeout=0.05)

            if key is not None:
                running = node.handle_key(key)
            else:
                node.publish_cmd()

    except KeyboardInterrupt:
        pass

    finally:
        node.stop()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
