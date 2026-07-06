# Gen Gripper Controller SDK (ROS2)

> 用于 Gen Controller 夹爪的 ROS2 驱动，支持相机图像、触觉传感、编码器反馈及开合距离控制。

[English](README.MD)

[GitHub代码](https://github.com/genrobot-ai/gen_con_sdk_ros2_release)

License: [MIT License](LICENSE) 

## 1 功能特性

- 三相机图像流，支持实时预览
- 触觉数据发布（左 / 右）
- 夹爪开合距离编码器反馈
- 通过 ROS 话题控制夹爪开合
- 单爪 / 双爪 launch 文件
- 标定、设备 ID、触觉调试等工具脚本

## 2 环境要求


| 项目     | 要求                  |
| ------ | ------------------- |
| 系统     | Ubuntu 24.04（推荐）    |
| ROS    | ROS2 Jazzy          |
| Python | 3.10+               |
| USB    | USB 3.0 接口          |
| 硬件     | Gen Controller 夹爪设备 |

## 3 快速开始


> 首次使用请先完成 [USB 配置](docs/usb-setup_CN.md)。

```shell
git clone https://github.com/genrobot-ai/gen_con_sdk_ros2_release.git
cd gen_con_sdk_ros2_release
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --base-paths src/robot_driver
source install/setup.bash
ros2 launch robot_driver single_gripper_start.launch.py
```

验证反馈并发送控制指令：

```shell
# 终端 2 — 读取编码器反馈
ros2 topic echo /encoder

# 终端 3 — 设置目标开合 5 cm（范围：0.0 ~ 0.103 m）
ros2 topic pub /target_distance std_msgs/msg/Float32 "{data: 0.05}" --once
```



## 4 ROS 话题



### 4.1 单爪


| Topic                       | 类型                        | 方向  | 说明                       |
| --------------------------- | ------------------------- | --- | ------------------------ |
| `/camera/color/image_raw`   | `sensor_msgs/Image`       | 发布  | 中间相机                     |
| `/camera_1/color/image_raw` | `sensor_msgs/Image`       | 发布  | 左侧相机                     |
| `/camera_2/color/image_raw` | `sensor_msgs/Image`       | 发布  | 右侧相机                     |
| `/encoder`                  | `std_msgs/Float32`        | 发布  | 夹爪开合距离反馈（m）              |
| `/tactile/left`             | `std_msgs/Int8MultiArray` | 发布  | 左侧触觉                     |
| `/tactile/right`            | `std_msgs/Int8MultiArray` | 发布  | 右侧触觉                     |
| `/target_distance`          | `std_msgs/Float32`        | 订阅  | 目标开合距离，范围 `[0.0, 0.103]` |




### 4.2 双爪

所有话题带 `/left_gripper` 或 `/right_gripper` 前缀，例如：


| Topic                            | 类型                 | 方向  | 说明      |
| -------------------------------- | ------------------ | --- | ------- |
| `/left_gripper/encoder`          | `std_msgs/Float32` | 发布  | 左夹爪开合反馈 |
| `/left_gripper/target_distance`  | `std_msgs/Float32` | 订阅  | 左夹爪目标距离 |
| `/right_gripper/encoder`         | `std_msgs/Float32` | 发布  | 右夹爪开合反馈 |
| `/right_gripper/target_distance` | `std_msgs/Float32` | 订阅  | 右夹爪目标距离 |


相机与触觉话题遵循相同命名空间规则（如 `/left_gripper/camera/...`、`/left_gripper/tactile/...`）。

## 5 安装



### 5.1 安装系统与 Python 依赖

```shell
sudo apt update
sudo apt install ros-jazzy-desktop python3-pip v4l-utils
pip3 install -r requirements.txt
```

`v4l-utils` 提供 USB 配置所需的 `v4l2-ctl` 命令。

### 5.2 拉取仓库并编译

```shell
git clone https://github.com/genrobot-ai/gen_con_sdk_ros2_release.git
cd gen_con_sdk_ros2_release
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install --base-paths src/robot_driver
source install/setup.bash
```

若需自动加载工作空间，可加入 `~/.bashrc`：

```shell
source /path/to/gen_con_sdk_ros2_release/install/setup.bash
```



## 6 USB 配置

首次使用前需为每个 USB 口配置 udev 规则，模板见 [config/99-usb-serial.rules](./config/99-usb-serial.rules)。

简要步骤：

1. 用 `udevadm` 和 `v4l2-ctl` 查询串口与相机的 `KERNELS` 值
2. 编辑 `config/99-usb-serial.rules`
3. 复制到 `/etc/udev/rules.d/` 并 reload

详细图文步骤见：

- [USB 配置指南 (ZH)](docs/usb-setup_CN.md)
- [USB Configuration Guide (EN)](docs/usb-setup.md)

双爪配置后的默认串口软链接：`/dev/ttyDeviceLeft`、`/dev/ttyDeviceRight`。

## 7 使用方法



### 7.1 单爪启动

```shell
source install/setup.bash
ros2 launch robot_driver single_gripper_start.launch.py
```

默认弹出三个预览窗口。关闭预览：

```shell
ros2 launch robot_driver single_gripper_start.launch.py show_preview:=false
```



### 7.2 双爪启动

```shell
source install/setup.bash
ros2 launch robot_driver dual_gripper_start.launch.py
```

运行 demo 节点，将模型指令桥接到夹爪话题：

```shell
ros2 run robot_driver left_das_controller_infer
ros2 run robot_driver right_das_controller_infer
```



### 7.3 设备工具命令

ROS2 不需要 `roscore`。**不要**在同一 USB 设备上同时运行多个设备指令。

**单设备：**

```shell
cd src/robot_driver/scripts/
bash camera_cmd.sh camerarc   # 中间相机标定
bash camera_cmd.sh camerarl   # 左侧相机标定
bash camera_cmd.sh camerarr   # 右侧相机标定
bash camera_cmd.sh MCUID      # 设备 ID
ros2 run robot_driver tactile_dual_print   # 打印触觉数据
```

**双设备（左 / 右）：**

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



## 8 常见问题


| 问题                | 解决方法                                                                                      |
| ----------------- | ----------------------------------------------------------------------------------------- |
| 找不到串口             | 执行 `sudo apt remove brltty`，重新插拔设备                                                        |
| 相机或串口路径不对         | 检查 udev 规则，见 [docs/usb-setup_CN.md](docs/usb-setup_CN.md)                                 |
| V4 Controller 帧率减半 | 在 launch 文件中设置 `fps: 60`，或启动后执行 `ros2 param set /camera fps 60`                          |
| 无 ROS 数据          | 确认驱动已启动且 udev 规则已加载                                                                      |
| `colcon build` 失败 | 确认已 source ROS2：`source /opt/ros/jazzy/setup.bash`                                        |




## 9 文档索引


| 说明 | 链接 |
| -------------- | ---------------------------------------------------------------------------------- |
| 用户手册 | [DAS Controller 用户手册](https://docs.genrobot.ai/zh/products/das-controller) |
| URDF | [URDF 模型](https://zcnma1sv5kma.feishu.cn/wiki/CKpbwye45iOlrckukIPc5hKCndh) |
| 问题解决指南 | [Gripper Controller 问题指南](https://zcnma1sv5kma.feishu.cn/docx/E6VJdNqIfoGrSDxKIHKck7tLn3b) |
| USB 配置 (ZH) | [docs/usb-setup_CN.md](docs/usb-setup_CN.md) |
| USB setup (EN) | [docs/usb-setup.md](docs/usb-setup.md)                                             |
| udev 规则模板      | [config/99-usb-serial.rules](config/99-usb-serial.rules)                           |
| 单爪 launch      | [single_gripper_start.launch.py](src/robot_driver/launch/single_gripper_start.launch.py) |
| 双爪 launch      | [dual_gripper_start.launch.py](src/robot_driver/launch/dual_gripper_start.launch.py)     |
| Demo 节点        | [src/robot_driver/robot_driver/](src/robot_driver/robot_driver/)                   |
| 设备脚本           | [src/robot_driver/scripts/](src/robot_driver/scripts/)                             |


