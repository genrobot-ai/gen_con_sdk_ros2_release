#!/usr/bin/env python3
"""ROS2 single-gripper launch."""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, TimerAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    serial_arg = DeclareLaunchArgument('serial', default_value='/dev/ttyDeviceLeft')
    gripper_type_arg = DeclareLaunchArgument('gripper_type', default_value='default_gripper')
    res_arg = DeclareLaunchArgument('camera_resolutions', default_value='1600x1296')
    preview_arg = DeclareLaunchArgument('show_preview', default_value='true')
    qos_reliability_arg = DeclareLaunchArgument('image_qos_reliability', default_value='best_effort')
    qos_depth_arg = DeclareLaunchArgument('image_qos_depth', default_value='1')

    v0m = DeclareLaunchArgument('video_0_main', default_value='/dev/left_video_0_main')
    v0s = DeclareLaunchArgument('video_0_sec', default_value='/dev/left_video_0_sec')
    v1m = DeclareLaunchArgument('video_1_main', default_value='/dev/left_video_1_main')
    v1s = DeclareLaunchArgument('video_1_sec', default_value='/dev/left_video_1_sec')
    v2m = DeclareLaunchArgument('video_2_main', default_value='/dev/left_video_2_main')
    v2s = DeclareLaunchArgument('video_2_sec', default_value='/dev/left_video_2_sec')

    serial = LaunchConfiguration('serial')
    gripper_type = LaunchConfiguration('gripper_type')
    res = LaunchConfiguration('camera_resolutions')
    show_preview = ParameterValue(LaunchConfiguration('show_preview'), value_type=bool)
    image_qos_depth = ParameterValue(LaunchConfiguration('image_qos_depth'), value_type=int)

    camera_node = Node(
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
            'usb_port': serial,
            'camera_count': 3,
            'fps': 30,
            'image_qos_reliability': LaunchConfiguration('image_qos_reliability'),
            'image_qos_depth': image_qos_depth,
            # Match original launch mapping: node's video_1_* <- video_2_*, video_2_* <- video_1_*
            'video_0_main': LaunchConfiguration('video_0_main'),
            'video_0_sec': LaunchConfiguration('video_0_sec'),
            'video_1_main': LaunchConfiguration('video_2_main'),
            'video_1_sec': LaunchConfiguration('video_2_sec'),
            'video_2_main': LaunchConfiguration('video_1_main'),
            'video_2_sec': LaunchConfiguration('video_1_sec'),
        }],
    )

    das_node = Node(
        package='robot_driver',
        executable='databus_single',
        name='das_node',
        output='screen',
        parameters=[{
            'serial_port': serial,
            'gripper_type': gripper_type,
            'topic_left_tactile': 'tactile/left',
            'topic_right_tactile': 'tactile/right',
            'topic_encoder': 'encoder',
            'topic_target_distance': 'target_distance',
        }],
    )

    return LaunchDescription([
        serial_arg, gripper_type_arg, res_arg, preview_arg, qos_reliability_arg, qos_depth_arg,
        v0m, v0s, v1m, v1s, v2m, v2s,
        camera_node,
        TimerAction(period=3.0, actions=[das_node]),
    ])
