#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Image


def _parse_reliability(value):
    value = str(value).strip().lower()
    if value in ('reliable', 'reliability_reliable'):
        return ReliabilityPolicy.RELIABLE
    return ReliabilityPolicy.BEST_EFFORT


def _stamp_to_sec(stamp):
    return float(stamp.sec) + float(stamp.nanosec) * 1e-9


def _summarize(samples):
    if not samples:
        return "n=0"

    n = len(samples)
    avg = sum(samples) / n
    min_v = min(samples)
    max_v = max(samples)
    if n > 1:
        var = sum((x - avg) * (x - avg) for x in samples) / n
        std = math.sqrt(var)
    else:
        std = 0.0

    hz = 1.0 / avg if avg > 0.0 else 0.0
    return (
        f"n={n} avg={avg * 1000.0:.2f}ms "
        f"hz={hz:.2f} min={min_v * 1000.0:.2f}ms "
        f"max={max_v * 1000.0:.2f}ms std={std * 1000.0:.2f}ms"
    )


class ImageTimingProbe(Node):
    def __init__(self):
        super().__init__('image_timing_probe')

        self.declare_parameter('topic', '/camera/color/image_raw')
        self.declare_parameter('window', 100)
        self.declare_parameter('log_period', 1.0)
        self.declare_parameter('reliability', 'best_effort')
        self.declare_parameter('depth', 1)

        self.topic = self.get_parameter('topic').value
        self.window = max(2, int(self.get_parameter('window').value))
        log_period = max(0.1, float(self.get_parameter('log_period').value))
        reliability = _parse_reliability(self.get_parameter('reliability').value)
        depth = max(1, int(self.get_parameter('depth').value))

        self.prev_header_ts = None
        self.prev_recv_ts = None
        self.header_dts = []
        self.recv_dts = []
        self.msg_count = 0

        qos = QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=depth,
            reliability=reliability,
        )
        self.create_subscription(Image, self.topic, self._on_image, qos)
        self.create_timer(log_period, self._on_timer)

        self.get_logger().info(
            f"Subscribing {self.topic} with {reliability.name} depth={depth}, window={self.window}"
        )

    def _on_image(self, msg):
        recv_ts = _stamp_to_sec(self.get_clock().now().to_msg())
        header_ts = _stamp_to_sec(msg.header.stamp)

        self.msg_count += 1

        if self.prev_header_ts is not None:
            header_dt = header_ts - self.prev_header_ts
            if header_dt >= 0.0:
                self.header_dts.append(header_dt)
                self.header_dts = self.header_dts[-self.window:]

        if self.prev_recv_ts is not None:
            recv_dt = recv_ts - self.prev_recv_ts
            if recv_dt >= 0.0:
                self.recv_dts.append(recv_dt)
                self.recv_dts = self.recv_dts[-self.window:]

        self.prev_header_ts = header_ts
        self.prev_recv_ts = recv_ts

    def _on_timer(self):
        self.get_logger().info(
            f"topic={self.topic} msgs={self.msg_count} | "
            f"header_dt: {_summarize(self.header_dts)} | "
            f"recv_dt: {_summarize(self.recv_dts)}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = ImageTimingProbe()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
