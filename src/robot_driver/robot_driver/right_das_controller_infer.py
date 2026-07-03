#!/usr/bin/env python3
# ROS2 port of right_das_controller_infer.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32


class GripperDataConverter(Node):
    def __init__(self):
        super().__init__('das_controller_converter')

        self.publish_rate = 100
        self.latest_right_data = None
        self.latest_right_cmd = None

        self.create_subscription(
            Float32, '/right_gripper/encoder', self.right_gripper_data_callback, 10)
        self.right_gripper_feedback_pub = self.create_publisher(
            PoseStamped, '/gripper/right/current_distance', 10)

        self.create_subscription(
            PoseStamped, '/target_gripper/right_gripper', self.right_cmd_callback, 10)
        self.right_gripper_cmd_pub = self.create_publisher(
            Float32, '/right_gripper/target_distance', 10)

        self.get_logger().debug("Gripper Data Converter Node Started")
        self.get_logger().debug(f"Publish rate: {self.publish_rate}Hz")

        period = 1.0 / self.publish_rate
        self.create_timer(period, self.publish_all_data)

    def right_gripper_data_callback(self, msg):
        self.latest_right_data = msg
        self.get_logger().info(f'right gripper distance: {msg.data:.4f} m')

    def process_gripper_feedback(self, gripper_msg, publisher, gripper_name):
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = f"{gripper_name}_gripper_frame"

        pose_msg.pose.position.x = float(gripper_msg.data)
        pose_msg.pose.position.y = 0.0
        pose_msg.pose.position.z = 0.0

        pose_msg.pose.orientation.x = 0.0
        pose_msg.pose.orientation.y = 0.0
        pose_msg.pose.orientation.z = 0.0
        pose_msg.pose.orientation.w = 1.0

        publisher.publish(pose_msg)

    def right_cmd_callback(self, msg):
        self.latest_right_cmd = msg

    def process_gripper_cmd(self, pos_msg, publisher, gripper_name):
        gripper_cmd_msg = Float32()
        gripper_cmd_msg.data = float(pos_msg.pose.position.x)
        publisher.publish(gripper_cmd_msg)

    def publish_all_data(self):
        if self.latest_right_data is not None:
            self.process_gripper_feedback(
                self.latest_right_data, self.right_gripper_feedback_pub, "right")
        if self.latest_right_cmd is not None:
            self.process_gripper_cmd(
                self.latest_right_cmd, self.right_gripper_cmd_pub, "right")
                
        # self.left_gripper_cmd_pub.publish(Float32(data=0.05))  # Control gripper target distance, range 0.0–0.103 m


def main(args=None):
    rclpy.init(args=args)
    node = GripperDataConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
