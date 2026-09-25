#!/usr/bin/env python3

import rclpy
from rclpy.node import Node

import board
import adafruit_dht

from sensor_msgs.msg import Temperature
from std_msgs.msg import Float32


class DHT11Node(Node):

    def __init__(self):
        super().__init__('dht11_node')

        self.temp_pub = self.create_publisher(
            Temperature,
            '/temperature',
            10
        )

        self.humidity_pub = self.create_publisher(
            Float32,
            '/humidity',
            10
        )

        self.timer = self.create_timer(
            2.0,
            self.publish_data
        )

        self.dht = adafruit_dht.DHT11(
            board.D4,
            use_pulseio=False
        )

        self.get_logger().info(
            "Geo X DHT11 Node Started"
        )

    def publish_data(self):

        try:

            temperature = self.dht.temperature
            humidity = self.dht.humidity

            if temperature is None or humidity is None:
                return

            temp_msg = Temperature()
            temp_msg.header.stamp = self.get_clock().now().to_msg()
            temp_msg.header.frame_id = "dht11_link"
            temp_msg.temperature = float(temperature)

            hum_msg = Float32()
            hum_msg.data = float(humidity)

            self.temp_pub.publish(temp_msg)
            self.humidity_pub.publish(hum_msg)

            self.get_logger().info(
                f"Temp: {temperature:.1f} °C | Humidity: {humidity:.1f}%"
            )

        except RuntimeError:
            pass

    def destroy_node(self):
        self.dht.exit()
        super().destroy_node()


def main(args=None):

    rclpy.init(args=args)

    node = DHT11Node()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
