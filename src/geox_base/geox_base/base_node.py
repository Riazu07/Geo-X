#!/usr/bin/env python3

import json
import threading
import time
import serial

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32, Int32
from geometry_msgs.msg import Vector3

class BaseNode(Node):

    def __init__(self):
        super().__init__("geox_base")

        self.port = "/dev/ttyUSB0"
        self.baud = 1000000

        self.left = 0.0
        self.right = 0.0

        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.05)
            self.get_logger().info(f"Connected to {self.port}")

        except Exception as e:
            self.get_logger().error(str(e))
            raise

        threading.Thread(target=self.receiver, daemon=True).start()
        threading.Thread(target=self.heartbeat, daemon=True).start()

        self.cmd_sub = self.create_subscription(
            Twist,
            "/cmd_vel",
            self.cmd_vel_callback,
            10
        )

        # Battery publishers
        self.voltage_pub = self.create_publisher(
            Float32,
            "/battery_voltage",
            10
        )

        self.battery_pub = self.create_publisher(
            Int32,
            "/battery_percentage",
            10
        )

        # Encoder publishers
        self.left_encoder_pub = self.create_publisher(
            Int32,
            "/encoder_left_count",
            10
        )

        self.right_encoder_pub = self.create_publisher(
            Int32,
            "/encoder_right_count",
            10
        )

        # Wheel RPM
        self.rpm_pub = self.create_publisher(
            Vector3,
            "/wheel_rpm",
            10
        )

        self.get_logger().info("Serial threads started")

    # --------------------------

    def heartbeat(self):

        while rclpy.ok():

            cmd = {
                "T": 1,
                "L": self.left,
                "R": self.right
            }

            try:
                self.ser.write(
                    (json.dumps(cmd) + "\n").encode()
                )

            except Exception:
                pass

            time.sleep(0.1)

    # --------------------------

    def receiver(self):

        while rclpy.ok():

            try:

                if not self.ser.in_waiting:
                    continue

                line = self.ser.readline().decode(
                    errors="ignore"
                ).strip()

                if not line:
                    continue

                try:

                    data = json.loads(line)

                    if data.get("T") == 100:

                        left_msg = Int32()
                        left_msg.data = data["left_count"]
                        self.left_encoder_pub.publish(left_msg)

                        right_msg = Int32()
                        right_msg.data = data["right_count"]
                        self.right_encoder_pub.publish(right_msg)

                        rpm = Vector3()
                        rpm.x = float(data["left_rpm"])
                        rpm.y = float(data["right_rpm"])
                        rpm.z = 0.0

                        self.rpm_pub.publish(rpm)

                    elif data.get("T") == 130:

                        voltage = Float32()
                        voltage.data = float(data["voltage"])
                        self.voltage_pub.publish(voltage)

                        battery = Int32()
                        battery.data = int(data["battery"])
                        self.battery_pub.publish(battery)

                except Exception:
                    pass

            except Exception:
                pass

    def cmd_vel_callback(self, msg):

        linear = msg.linear.x
        angular = msg.angular.z

        # Simple differential drive mixing
        left = linear - angular
        right = linear + angular

        # Clamp to [-1.0, 1.0]
        left = max(min(left, 1.0), -1.0)
        right = max(min(right, 1.0), -1.0)

        self.left = left
        self.right = right

        self.get_logger().info(
            f"CMD -> L:{left:.2f}  R:{right:.2f}"
        )

def main(args=None):

    rclpy.init(args=args)

    node = BaseNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
