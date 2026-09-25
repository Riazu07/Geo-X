#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from adafruit_servokit import ServoKit
from std_msgs.msg import Int32MultiArray


class ArmNode(Node):

    def __init__(self):

        super().__init__("geox_arm")

        self.kit = ServoKit(channels=16)

        self.angles = [90] * 6
        self.move = [0] * 6
        self.step = 1

        for i in range(6):
            self.kit.servo[i].angle = self.angles[i]

        self.get_logger().info("Geo X Arm Driver Started")
        self.get_logger().info("All servos initialized to 90°")

        self.arm_sub = self.create_subscription(
            Int32MultiArray,
            "/arm_cmd",
            self.arm_callback,
            10
        )

        self.timer = self.create_timer(
            0.02,
            self.update_servos
        )

    def destroy_node(self):

        for i in range(6):
            self.kit.servo[i].angle = None

        super().destroy_node()

    def arm_callback(self, msg):

        if len(msg.data) != 6:
           return

        self.move = list(msg.data)

    def update_servos(self):

        for i in range(6):

            if self.move[i] == 0:
                continue

            new_angle = self.angles[i] + self.move[i] * self.step

            new_angle = max(0, min(180, new_angle))

            if new_angle != self.angles[i]:

                self.angles[i] = new_angle

                self.kit.servo[i].angle = self.angles[i]

def main(args=None):

    rclpy.init(args=args)

    node = ArmNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
