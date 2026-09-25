#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32

import serial
import json
import threading


class INA219Node(Node):

    def __init__(self):
        super().__init__("ina219_node")

        # Initialize INA219
        self.serial = serial.Serial(
            "/dev/ttyUSB0",
            1000000,
            timeout=1
        )

        # Publishers
        self.voltage_pub = self.create_publisher(
            Float32,
            "/battery_voltage",
            10
        )

        self.percent_pub = self.create_publisher(
            Float32,
            "/battery_percentage",
            10
        )


        self.get_logger().info("Geo X INA219 Node Started")

        self.serial_thread = threading.Thread(
          target=self.serial_loop,
          daemon=True
       )

        self.serial_thread.start()

    def serial_loop(self):

        while rclpy.ok():

            try:

                line = self.serial.readline().decode(
                    "utf-8",
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                # Uncomment this for debugging
                # self.get_logger().info(f"RAW: {line}")

                try:
                    data = json.loads(line)

                except json.JSONDecodeError:
                    continue

                voltage = data.get("voltage")
                battery = data.get("battery")

                if voltage is None or battery is None:
                    continue

                voltage_msg = Float32()
                percent_msg = Float32()

                voltage_msg.data = float(voltage)
                percent_msg.data = float(battery)

                self.voltage_pub.publish(voltage_msg)
                self.percent_pub.publish(percent_msg)

                self.get_logger().info(
                    f"Voltage: {float(voltage):.2f} V | Battery: {float(battery):.1f}%"
                )

            except Exception as e:
                self.get_logger().error(str(e))

def main(args=None):

    rclpy.init(args=args)

    node = INA219Node()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()

