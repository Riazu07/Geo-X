#!/usr/bin/env python3

import time

from smbus2 import SMBus

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Imu
from sensor_msgs.msg import MagneticField


# -----------------------------
# MPU9250 Registers
# -----------------------------

MPU_ADDR = 0x68

PWR_MGMT_1 = 0x6B
INT_PIN_CFG = 0x37

ACCEL_XOUT_H = 0x3B
GYRO_XOUT_H = 0x43

AK8963_ADDR = 0x0C

AK8963_CNTL1 = 0x0A
AK8963_ST1 = 0x02
AK8963_ST2 = 0x09
AK8963_XOUT_L = 0x03


class IMUNode(Node):

    def __init__(self):

        super().__init__("imu_node")

        # Open I2C bus
        self.bus = SMBus(1)

        # Wake MPU9250
        self.bus.write_byte_data(MPU_ADDR, PWR_MGMT_1, 0x00)

        time.sleep(0.1)

        # Enable I2C bypass
        self.bus.write_byte_data(MPU_ADDR, INT_PIN_CFG, 0x02)

        time.sleep(0.1)

        # Configure AK8963
        self.bus.write_byte_data(AK8963_ADDR, AK8963_CNTL1, 0x00)

        time.sleep(0.1)

        self.bus.write_byte_data(AK8963_ADDR, AK8963_CNTL1, 0x16)

        time.sleep(0.1)

        self.get_logger().info("Geo X IMU Initialized")

        # Publisher for IMU
        self.imu_pub = self.create_publisher(
            Imu,
            "/imu/data",
            10
        )

        # Publisher for Magnetometer
        self.mag_pub = self.create_publisher(
            MagneticField,
            "/imu/mag",
            10
        )
        # Read sensor every 0.5 seconds
        self.timer = self.create_timer(
            0.5,
            self.timer_callback
        )

    def read_word(self, reg):

        high = self.bus.read_byte_data(MPU_ADDR, reg)
        low = self.bus.read_byte_data(MPU_ADDR, reg + 1)

        value = (high << 8) | low

        if value >= 0x8000:
            value = -((65535 - value) + 1)

        return value

    def read_mag_word(self, reg):

        low = self.bus.read_byte_data(AK8963_ADDR, reg)
        high = self.bus.read_byte_data(AK8963_ADDR, reg + 1)

        value = (high << 8) | low

        if value >= 32768:
            value -= 65536

        return value

    def read_imu(self):

        # Accelerometer
        ax = self.read_word(ACCEL_XOUT_H)
        ay = self.read_word(ACCEL_XOUT_H + 2)
        az = self.read_word(ACCEL_XOUT_H + 4)

        # Gyroscope
        gx = self.read_word(GYRO_XOUT_H)
        gy = self.read_word(GYRO_XOUT_H + 2)
        gz = self.read_word(GYRO_XOUT_H + 4)

        # Convert
        ax /= 16384.0
        ay /= 16384.0
        az /= 16384.0

        gx /= 131.0
        gy /= 131.0
        gz /= 131.0

        # Magnetometer
        status = self.bus.read_byte_data(AK8963_ADDR, AK8963_ST1)

        if status & 0x01:

            mx = self.read_mag_word(AK8963_XOUT_L)
            my = self.read_mag_word(AK8963_XOUT_L + 2)
            mz = self.read_mag_word(AK8963_XOUT_L + 4)

            # IMPORTANT
            self.bus.read_byte_data(AK8963_ADDR, AK8963_ST2)

        else:

            mx = my = mz = 0

        return ax, ay, az, gx, gy, gz, mx, my, mz

    def timer_callback(self):

        ax, ay, az, gx, gy, gz, mx, my, mz = self.read_imu()

        imu_msg = Imu()

        # Orientation not estimated yet
        imu_msg.orientation_covariance[0] = -1.0

        # Angular velocity covariance
        imu_msg.angular_velocity_covariance[0] = 0.001
        imu_msg.angular_velocity_covariance[4] = 0.001
        imu_msg.angular_velocity_covariance[8] = 0.001

        # Linear acceleration covariance
        imu_msg.linear_acceleration_covariance[0] = 0.01
        imu_msg.linear_acceleration_covariance[4] = 0.01
        imu_msg.linear_acceleration_covariance[8] = 0.01

        imu_msg.header.stamp = self.get_clock().now().to_msg()
        imu_msg.header.frame_id = "imu_link"

        # Linear acceleration
        imu_msg.linear_acceleration.x = ax
        imu_msg.linear_acceleration.y = ay
        imu_msg.linear_acceleration.z = az

        # Angular velocity
        imu_msg.angular_velocity.x = gx
        imu_msg.angular_velocity.y = gy
        imu_msg.angular_velocity.z = gz

        self.imu_pub.publish(imu_msg)

        mag_msg = MagneticField()

        mag_msg.magnetic_field_covariance[0] = 0.01
        mag_msg.magnetic_field_covariance[4] = 0.01
        mag_msg.magnetic_field_covariance[8] = 0.01

        mag_msg.header.stamp = imu_msg.header.stamp
        mag_msg.header.frame_id = "imu_link"

        # Convert µT to Tesla
        mag_msg.magnetic_field.x = float(mx) * 1e-6
        mag_msg.magnetic_field.y = float(my) * 1e-6
        mag_msg.magnetic_field.z = float(mz) * 1e-6

        self.mag_pub.publish(mag_msg)

        self.get_logger().info(
            "Publishing IMU Data..."
        )

def main(args=None):

    rclpy.init(args=args)

    node = IMUNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
