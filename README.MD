# Gen Controller SDK (ROS2)

> ROS2 driver for Gen Controller gripper — camera streaming, tactile sensing, encoder feedback, and distance control.

[中文](README(ZH).MD)

[GitHub repository](https://github.com/genrobot-ai/gen_con_sdk_ros2_release)

License: [MIT License](LICENSE)

## 1 Features

- Three-camera image streaming with optional live preview
- Tactile sensor data publishing (left / right)
- Encoder feedback for gripper opening distance
- Gripper distance control via ROS topics
- Single-gripper and dual-gripper launch files
- Utility scripts for calibration, device ID, and tactile debugging

## 2 Requirements


| Item     | Requirement                   |
| -------- | ----------------------------- |
| OS       | Ubuntu 24.04 (recommended)    |
| ROS      | ROS2 Jazzy                    |
| Python   | 3.10+                         |
| USB      | USB 3.0 port                  |
| Hardware | Gen Controller gripper device |




## 3 Quick Start

> First-time users must complete [USB configuration](docs/usb-setup.md) before launching the driver.

```shell
git clone https://github.com/genrobot-ai/gen_con_sdk_ros2_release.git
cd gen_con_sdk_ros2_release
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --base-paths src/robot_driver
source install/setup.bash
ros2 launch robot_driver single_gripper_start.launch.py
```

Verify feedback and send a control command:

```shell
# Terminal 2 — read encoder feedback
ros2 topic echo /encoder

# Terminal 3 — set target opening to 5 cm (range: 0.0 ~ 0.103 m)
ros2 topic pub /target_distance std_msgs/msg/Float32 "{data: 0.05}" --once
```



## 4 ROS Topics



### 4.1 Single Gripper


| Topic                       | Type                      | Direction | Description                                   |
| --------------------------- | ------------------------- | --------- | --------------------------------------------- |
| `/camera/color/image_raw`   | `sensor_msgs/Image`       | publish   | Center camera                                 |
| `/camera_1/color/image_raw` | `sensor_msgs/Image`       | publish   | Left-side camera                              |
| `/camera_2/color/image_raw` | `sensor_msgs/Image`       | publish   | Right-side camera                             |
| `/encoder`                  | `std_msgs/Float32`        | publish   | Gripper opening distance feedback (m)         |
| `/tactile/left`             | `std_msgs/Int8MultiArray` | publish   | Left tactile sensor                           |
| `/tactile/right`            | `std_msgs/Int8MultiArray` | publish   | Right tactile sensor                          |
| `/target_distance`          | `std_msgs/Float32`        | subscribe | Target opening distance, range `[0.0, 0.103]` |




### 4.2 Dual Gripper

All topics are prefixed with `/left_gripper` or `/right_gripper`. For example:


| Topic                            | Type               | Direction | Description                    |
| -------------------------------- | ------------------ | --------- | ------------------------------ |
| `/left_gripper/encoder`          | `std_msgs/Float32` | publish   | Left gripper opening feedback  |
| `/left_gripper/target_distance`  | `std_msgs/Float32` | subscribe | Left gripper target distance   |
| `/right_gripper/encoder`         | `std_msgs/Float32` | publish   | Right gripper opening feedback |
| `/right_gripper/target_distance` | `std_msgs/Float32` | subscribe | Right gripper target distance  |


Camera and tactile topics follow the same namespace pattern (`/left_gripper/camera/...`, `/left_gripper/tactile/...`, etc.).

## 5 Installation



### 5.1 Install system and Python dependencies

```shell
sudo apt update
sudo apt install ros-jazzy-desktop python3-pip v4l-utils
pip3 install -r requirements.txt
```

`v4l-utils` provides `v4l2-ctl`, required for USB configuration.

### 5.2 Clone and build

```shell
git clone https://github.com/genrobot-ai/gen_con_sdk_ros2_release.git
cd gen_con_sdk_ros2_release
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --base-paths src/robot_driver
source install/setup.bash
```

To load the workspace automatically, add to `~/.bashrc`:

```shell
source /path/to/gen_con_sdk_ros2_release/install/setup.bash
```



## 6 USB Configuration

Configure udev rules once per USB port before first use. The template is at [config/99-usb-serial.rules](./config/99-usb-serial.rules).

Summary:

1. Query serial and camera `KERNELS` values with `udevadm` and `v4l2-ctl`
2. Edit `config/99-usb-serial.rules`
3. Copy to `/etc/udev/rules.d/` and reload rules

For step-by-step instructions with screenshots, see:

- [USB 配置指南 (ZH)](docs/usb-setup_CN.md)
- [USB Configuration Guide (EN)](docs/usb-setup.md)

Default serial symlinks after dual-gripper setup: `/dev/ttyDeviceLeft`, `/dev/ttyDeviceRight`.

## 7 Usage



### 7.1 Single Gripper

```shell
source install/setup.bash
ros2 launch robot_driver single_gripper_start.launch.py
```

Three preview windows appear by default. Disable preview:

```shell
ros2 launch robot_driver single_gripper_start.launch.py show_preview:=false
```



### 7.2 Dual Gripper

```shell
source install/setup.bash
ros2 launch robot_driver dual_gripper_start.launch.py
```

Run demo nodes to bridge model commands to gripper topics:

```shell
ros2 run robot_driver left_das_controller_infer
ros2 run robot_driver right_das_controller_infer
```



### 7.3 Device Utilities

ROS2 does not require `roscore`. Do **not** run multiple device commands simultaneously on the same USB device.

**Single device:**

```shell
cd src/robot_driver/scripts/
bash camera_cmd.sh camerarc   # Center camera calibration
bash camera_cmd.sh camerarl   # Left camera calibration
bash camera_cmd.sh camerarr   # Right camera calibration
bash camera_cmd.sh MCUID      # Device ID
ros2 run robot_driver tactile_dual_print   # Print tactile data
```

**Dual device (left / right):**

```shell
cd src/robot_driver/scripts/

bash camera_cmd.sh left camerarc
bash camera_cmd.sh left camerarl
bash camera_cmd.sh left camerarr
bash camera_cmd.sh left MCUID
ros2 run robot_driver tactile_dual_print --ros-args -p gripper_ns:=left_gripper

bash camera_cmd.sh right camerarc
bash camera_cmd.sh right camerarl
bash camera_cmd.sh right camerarr
bash camera_cmd.sh right MCUID
ros2 run robot_driver tactile_dual_print --ros-args -p gripper_ns:=right_gripper
```



## 8 Troubleshooting


| Problem                         | Solution                                                                                      |
| ------------------------------- | --------------------------------------------------------------------------------------------- |
| Serial port not found           | Run `sudo apt remove brltty`, then replug the device                                          |
| Camera or serial has wrong path | Re-check udev rules; see [docs/usb-setup.md](docs/usb-setup.md)                             |
| V4 Controller frame rate halved | Set `fps: 60` in the launch file or run `ros2 param set /camera fps 60` after startup         |
| No ROS data                     | Ensure the driver is launched and udev rules are loaded                                       |
| `colcon build` fails            | Confirm ROS2 Jazzy is sourced: `source /opt/ros/jazzy/setup.bash`                           |




## 9 Documentation


| Description           | Link                                                                                     |
| --------------------- | ---------------------------------------------------------------------------------------- |
| User Manual           | [DAS Controller User Manual](https://docs.genrobot.ai/en/products/das-controller)        |
| URDF                  | [URDF Model](https://zcnma1sv5kma.feishu.cn/wiki/CKpbwye45iOlrckukIPc5hKCndh)            |
| Troubleshooting Guide | [Problem Solving Guide](https://zcnma1sv5kma.feishu.cn/docx/E6VJdNqIfoGrSDxKIHKck7tLn3b) |
| USB 配置 (ZH)           | [docs/usb-setup_CN.md](docs/usb-setup_CN.md)                                             |
| USB setup (EN)        | [docs/usb-setup.md](docs/usb-setup.md)                                                   |
| udev rules template   | [config/99-usb-serial.rules](config/99-usb-serial.rules)                                 |
| Single gripper launch | [single_gripper_start.launch.py](src/robot_driver/launch/single_gripper_start.launch.py) |
| Dual gripper launch   | [dual_gripper_start.launch.py](src/robot_driver/launch/dual_gripper_start.launch.py)     |
| Demo nodes            | [src/robot_driver/robot_driver/](src/robot_driver/robot_driver/)                         |
| Device scripts        | [src/robot_driver/scripts/](src/robot_driver/scripts/)                                   |
