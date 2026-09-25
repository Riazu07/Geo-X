#!/usr/bin/env python3

import serial
import pynmea2

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import NavSatFix, NavSatStatus
from std_msgs.msg import String


class GPSNode(Node):

    def __init__(self):
        super().__init__("gps_node")

        self.get_logger().info("Geo X GPS Node Started")

        # -----------------------------
        # Open Serial Port
        # -----------------------------
        self.serial = serial.Serial(
            port="/dev/ttyAMA0",
            baudrate=9600,
            timeout=1
        )

        # -----------------------------
        # Publishers
        # -----------------------------
        self.fix_pub = self.create_publisher(
            NavSatFix,
            "/gps/fix",
            10
        )

        self.status_pub = self.create_publisher(
            String,
            "/gps/status",
            10
        )

        # -----------------------------
        # Read GPS every 100 ms
        # -----------------------------
        self.timer = self.create_timer(
            0.1,
            self.read_gps
        )

    def safe_float(self, value, default=0.0):
        """
        Safely convert any GPS field to float.
        Prevents NavSatFix crashes.
        """
        try:
            if value is None:
                return default

            if value == "":
                return default

            return float(value)

        except Exception:
            return default

    def read_gps(self):

        try:

            line = self.serial.readline().decode(
                "ascii",
                errors="replace"
            ).strip()

            if not line.startswith("$"):
                return

            msg = pynmea2.parse(line)

# -----------------------------
            # GGA Message
            # -----------------------------
            if isinstance(msg, pynmea2.types.talker.GGA):

                fix = NavSatFix()

                # Timestamp
                fix.header.stamp = self.get_clock().now().to_msg()
                fix.header.frame_id = "gps_link"

                # Fix status
                if int(msg.gps_qual or 0) > 0:
                    fix.status.status = NavSatStatus.STATUS_FIX
                else:
                    fix.status.status = NavSatStatus.STATUS_NO_FIX

                fix.status.service = NavSatStatus.SERVICE_GPS

                # Safe coordinates
                fix.latitude = self.safe_float(msg.latitude)
                fix.longitude = self.safe_float(msg.longitude)
                fix.altitude = self.safe_float(msg.altitude)

                # Covariance (unknown)
                fix.position_covariance = [
                    0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0,
                    0.0, 0.0, 0.0
                ]

                fix.position_covariance_type = (
                    NavSatFix.COVARIANCE_TYPE_UNKNOWN
                )

                self.fix_pub.publish(fix)

                status = String()

                if int(msg.gps_qual or 0) == 0:
                    status.data = "NO FIX"

                elif int(msg.gps_qual or 0) == 1:
                    status.data = "GPS FIX"

                elif int(msg.gps_qual or 0) == 2:
                    status.data = "DGPS FIX"

                else:
                    status.data = f"FIX TYPE {msg.gps_qual}"

                self.status_pub.publish(status)

                self.get_logger().info(
                    f"Lat: {fix.latitude:.6f}, "
                    f"Lon: {fix.longitude:.6f}, "
                    f"Alt: {fix.altitude:.2f} m | "
                    f"{status.data}"
                )
        except Exception as e:
          self.get_logger().error(str(e))


def main(args=None):
    rclpy.init(args=args)

    node = GPSNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
