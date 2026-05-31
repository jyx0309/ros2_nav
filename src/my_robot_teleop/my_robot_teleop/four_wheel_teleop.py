import math
import select
import sys
import termios
import time
import tty

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


HELP_TEXT = """
Four-wheel teleop started.
--------------------------
w: increase forward speed
s: increase backward speed
a: steer left
d: steer right
c: center steering
x: stop
q: quit
"""


class FourWheelTeleop(Node):
    def __init__(self):
        super().__init__('four_wheel_teleop')

        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.linear_x = 0.0
        self.steering_angle = 0.0

        self.linear_step = 0.05
        self.steering_step = 0.10

        self.max_linear = 0.25
        self.max_steering_angle = 0.55
        self.wheelbase = 0.42

        self.get_logger().info(HELP_TEXT)

    def angular_z(self):
        if abs(self.linear_x) < 1e-6:
            return 0.0
        return self.linear_x * math.tan(self.steering_angle) / self.wheelbase

    def publish_cmd(self):
        msg = Twist()
        msg.linear.x = self.linear_x
        msg.angular.z = self.angular_z()
        self.cmd_pub.publish(msg)

    def stop(self):
        self.linear_x = 0.0
        self.steering_angle = 0.0
        self.publish_cmd()

    def ramp_stop(self, steps=10, delay=0.03):
        start_linear = self.linear_x
        start_steering = self.steering_angle

        for step in range(steps - 1, -1, -1):
            scale = step / steps
            self.linear_x = start_linear * scale
            self.steering_angle = start_steering * scale
            self.publish_cmd()
            time.sleep(delay)

    def handle_key(self, key):
        if key == 'w':
            self.linear_x = min(self.linear_x + self.linear_step, self.max_linear)
        elif key == 's':
            self.linear_x = max(self.linear_x - self.linear_step, -self.max_linear)
        elif key == 'a':
            self.steering_angle = min(
                self.steering_angle + self.steering_step,
                self.max_steering_angle
            )
        elif key == 'd':
            self.steering_angle = max(
                self.steering_angle - self.steering_step,
                -self.max_steering_angle
            )
        elif key == 'c':
            self.steering_angle = 0.0
        elif key == 'x':
            self.ramp_stop()
        elif key == 'q':
            self.ramp_stop()
            return False

        self.publish_cmd()
        self.get_logger().info(
            'linear.x={:.2f}, steering={:.2f} rad, angular.z={:.2f}'.format(
                self.linear_x,
                self.steering_angle,
                self.angular_z()
            )
        )
        return True


def get_key(timeout=0.1):
    rlist, _, _ = select.select([sys.stdin], [], [], timeout)
    if rlist:
        return sys.stdin.read(1)
    return None


def main(args=None):
    rclpy.init(args=args)
    node = FourWheelTeleop()

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
