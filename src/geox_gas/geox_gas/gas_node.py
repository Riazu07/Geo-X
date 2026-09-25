#!/usr/bin/env python3

import time
import gpiod

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from std_msgs.msg import Bool


GPIO_CHIP = "/dev/gpiochip4"
GPIO_LINE = 23


class GasNode(Node):

    def __init__(self):
        super().__init__("gas_node")

        self.status_pub = self.create_publisher(
            String,
            "/gas/status",
            10
        )

        self.detect_pub = self.create_publisher(
            Bool,
            "/gas/detected",
            10
        )

        self.chip = gpiod.Chip(GPIO_CHIP)

        self.request = self.chip.request_lines(
            config={
                GPIO_LINE: gpiod.LineSettings(
                    direction=gpiod.line.Direction.INPUT
                )
            },
            consumer="GEOX_GAS"
        )

        self.previous_state = None

        self.timer = self.create_timer(
            0.5,
            self.read_sensor
        )

        self.get_logger().info("Geo X MQ135 Node Started")
    def read_sensor(self):

        value = self.request.get_value(GPIO_LINE)

        gas_detected = (
            value == gpiod.line.Value.INACTIVE
        )

        status_msg = String()
        detect_msg = Bool()

        if gas_detected:
            status_msg.data = "Hazardous Gas Detected"
            detect_msg.data = True
        else:
            status_msg.data = "Air Quality Normal"
            detect_msg.data = False

        self.status_pub.publish(status_msg)
        self.detect_pub.publish(detect_msg)

        if self.previous_state != gas_detected:

            if gas_detected:
                self.get_logger().warn(
                    "⚠ Hazardous Gas Detected"
                )
            else:
                self.get_logger().info(
                    "✅ Air Quality Normal"
                )

            self.previous_state = gas_detected
def main(args=None):

    rclpy.init(args=args)

    node = GasNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.request.release()
        node.destroy_node()

        if rcply.ok():
            rcply.shutdown()


if __name__ == "__main__":
    main()
