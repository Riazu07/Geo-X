#!/usr/bin/env python3

import pygame

import rclpy
from rclpy.node import Node

from std_msgs.msg import Int32MultiArray


class ArmTeleop(Node):

    def __init__(self):

        super().__init__("geox_arm_teleop")

        self.pub = self.create_publisher(
            Int32MultiArray,
            "/arm_cmd",
            10
        )

        pygame.init()

        self.screen = pygame.display.set_mode((400,200))
        pygame.display.set_caption("Geo X Arm Teleop")

        self.move = [0] * 6

        self.timer = self.create_timer(
            0.02,
            self.publish_cmd
        )

        self.get_logger().info("Geo X Arm Teleop Started")

    def publish_cmd(self):

        msg = Int32MultiArray()

        msg.data = self.move

        self.pub.publish(msg)

    def process_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                rclpy.shutdown()

            # ---------------- KEY DOWN ----------------

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_1: self.move[0] = 1
                if event.key == pygame.K_2: self.move[0] = -1

                if event.key == pygame.K_q: self.move[1] = 1
                if event.key == pygame.K_w: self.move[1] = -1

                if event.key == pygame.K_a: self.move[2] = 1
                if event.key == pygame.K_s: self.move[2] = -1

                if event.key == pygame.K_z: self.move[3] = 1
                if event.key == pygame.K_x: self.move[3] = -1

                if event.key == pygame.K_e: self.move[4] = 1
                if event.key == pygame.K_r: self.move[4] = -1

                if event.key == pygame.K_t: self.move[5] = 1
                if event.key == pygame.K_y: self.move[5] = -1

                if event.key == pygame.K_c:
                    self.move = [0] * 6

            # ---------------- KEY UP ----------------

            if event.type == pygame.KEYUP:

                if event.key in [pygame.K_1, pygame.K_2]:
                    self.move[0] = 0

                if event.key in [pygame.K_q, pygame.K_w]:
                    self.move[1] = 0

                if event.key in [pygame.K_a, pygame.K_s]:
                    self.move[2] = 0

                if event.key in [pygame.K_z, pygame.K_x]:
                    self.move[3] = 0

                if event.key in [pygame.K_e, pygame.K_r]:
                    self.move[4] = 0

                if event.key in [pygame.K_t, pygame.K_y]:
                    self.move[5] = 0


def main(args=None):

    rclpy.init(args=args)

    node = ArmTeleop()

    while rclpy.ok():

        node.process_events()

        rclpy.spin_once(node, timeout_sec=0.01)

    pygame.quit()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
