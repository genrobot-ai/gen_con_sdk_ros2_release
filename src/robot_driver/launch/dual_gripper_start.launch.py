#!/usr/bin/env python3
"""ROS2 dual-gripper launch."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    left_serial = DeclareLaunchArgument('left_serial', default_value='/dev/ttyDeviceLeft')
    right_serial = DeclareLaunchArgument('right_serial', default_value='/dev/ttyDeviceRight')
    res_arg = DeclareLaunchArgument('camera_resolutions', default_value='1600x1296')
    preview_arg = DeclareLaunchArgument('show_preview', default_value='true')
    qos_reliability_arg = DeclareLaunchArgument('image_qos_reliability', default_value='best_effort')
    qos_depth_arg = DeclareLaunchArgument('image_qos_depth', default_value='1')

    left_videos = [
        DeclareLaunchArgument('left_video_0_main', default_value='/dev/left_video_0_main'),
        DeclareLaunchArgument('left_video_0_sec', default_value='/dev/left_video_0_sec'),
        DeclareLaunchArgument('left_video_1_main', default_value='/dev/left_video_1_main'),
        DeclareLaunchArgument('left_video_1_sec', default_value='/dev/left_video_1_sec'),
        DeclareLaunchArgument('left_video_2_main', default_value='/dev/left_video_2_main'),
        DeclareLaunchArgument('left_video_2_sec', default_value='/dev/left_video_2_sec'),
    ]
    right_videos = [
        DeclareLaunchArgument('right_video_0_main', default_value='/dev/right_video_0_main'),
        DeclareLaunchArgument('right_video_0_sec', default_value='/dev/right_video_0_sec'),
        DeclareLaunchArgument('right_video_1_main', default_value='/dev/right_video_1_main'),
        DeclareLaunchArgument('right_video_1_sec', default_value='/dev/right_video_1_sec'),
        DeclareLaunchArgument('right_video_2_main', default_value='/dev/right_video_2_main'),
        DeclareLaunchArgument('right_video_2_sec', default_value='/dev/right_video_2_sec'),
    ]

    show_preview = ParameterValue(LaunchConfiguration('show_preview'), value_type=bool)
    image_qos_depth = ParameterValue(LaunchConfiguration('image_qos_depth'), value_type=int)
    res = LaunchConfiguration('camera_resolutions')

    def side_group(ns, serial_cfg, v0m, v0s, v1m, v1s, v2m, v2s, das_delay):
        camera = Node(
            package='robot_driver',
            executable='camera_view_single',
            name='camera',
            output='screen',
            additional_env={
                'LIBGL_ALWAYS_SOFTWARE': '1',
                'MESA_LOADER_DRIVER_OVERRIDE': 'llvmpipe',
                'QT_OPENGL': 'software',
                'QT_XCB_GL_INTEGRATION': 'none',
            },
            parameters=[{
                'resolutions': res,
                'topic_base': 'camera',
                'show_preview': show_preview,
                'usb_port': serial_cfg,
                'camera_count': 3,
                'fps': 30,
                'image_qos_reliability': LaunchConfiguration('image_qos_reliability'),
                'image_qos_depth': image_qos_depth,
                'video_0_main': v0m,
                'video_0_sec': v0s,
                'video_1_main': v2m,
                'video_1_sec': v2s,
                'video_2_main': v1m,
                'video_2_sec': v1s,
            }],
        )
        das = Node(
            package='robot_driver',
            executable='databus_single',
            name='das_node',
            output='screen',
            parameters=[{
                'serial_port': serial_cfg,
                'topic_left_tactile': 'tactile/left',
                'topic_right_tactile': 'tactile/right',
                'topic_encoder': 'encoder',
                'topic_target_distance': 'target_distance',
            }],
        )
        return GroupAction(actions=[
            PushRosNamespace(ns),
            camera,
            TimerAction(period=das_delay, actions=[das]),
        ])

    left_group = side_group(
        'left_gripper', LaunchConfiguration('left_serial'),
        LaunchConfiguration('left_video_0_main'), LaunchConfiguration('left_video_0_sec'),
        LaunchConfiguration('left_video_1_main'), LaunchConfiguration('left_video_1_sec'),
        LaunchConfiguration('left_video_2_main'), LaunchConfiguration('left_video_2_sec'),
        das_delay=3.0,
    )
    right_group = side_group(
        'right_gripper', LaunchConfiguration('right_serial'),
        LaunchConfiguration('right_video_0_main'), LaunchConfiguration('right_video_0_sec'),
        LaunchConfiguration('right_video_1_main'), LaunchConfiguration('right_video_1_sec'),
        LaunchConfiguration('right_video_2_main'), LaunchConfiguration('right_video_2_sec'),
        das_delay=5.0,
    )

    return LaunchDescription([
        left_serial, right_serial, res_arg, preview_arg, qos_reliability_arg, qos_depth_arg,
        *left_videos, *right_videos,
        left_group, right_group,
    ])
