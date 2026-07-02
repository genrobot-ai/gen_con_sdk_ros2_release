#!/usr/bin/env bash
set -euo pipefail

# ROS2 wrapper around `ros2 run robot_driver camera_calib_cmd`.
#
# Usage examples:
#   Single device:
#     bash camera_cmd.sh 1234
#     bash camera_cmd.sh camerarc
#     bash camera_cmd.sh camerarl
#     bash camera_cmd.sh camerarr
#     bash camera_cmd.sh MCUID
#     bash camera_cmd.sh DMZEROSET
#   Dual device (left/right):
#     bash camera_cmd.sh left camerarc
#     bash camera_cmd.sh right camerarl
#     bash camera_cmd.sh left DMZEROSET
# Optional: set SERIAL_PORT to force a device; otherwise auto-find /dev/ttyUSB*.

usage() {
  echo "Usage:"
  echo "  Single: bash ${BASH_SOURCE[0]} {1234|camerarc|camerarl|camerarr|MCUID|DMZEROSET}"
  echo "  Dual:   bash ${BASH_SOURCE[0]} {left|right} {camerarc|camerarl|camerarr|MCUID|DMZEROSET|1234}"
  echo "Optional env: SERIAL_PORT=/dev/ttyUSB0"
  exit 1
}

if [[ $# -eq 1 ]]; then
  SIDE=""
  RECORD_VALUE="$1"
elif [[ $# -eq 2 ]]; then
  SIDE="$1"
  RECORD_VALUE="$2"
  if [[ "${SIDE}" != "left" && "${SIDE}" != "right" ]]; then
    echo "Error: first argument must be 'left' or 'right'"
    usage
  fi
else
  usage
fi

case "${RECORD_VALUE}" in
  1234|camerarc|camerarl|camerarr|MCUID|DMZEROSET) ;;
  *)
    echo "Error: second argument must be one of 1234/camerarc/camerarl/camerarr/MCUID/DMZEROSET"
    usage
    ;;
esac

SERIAL_PORT="${SERIAL_PORT:-}"

if [[ -z "${SERIAL_PORT}" ]]; then
  if [[ "${SIDE}" == "left" ]]; then
    SERIAL_PORT="/dev/ttyDeviceLeft"
  elif [[ "${SIDE}" == "right" ]]; then
    SERIAL_PORT="/dev/ttyDeviceRight"
  fi
  echo "Using default device: ${SERIAL_PORT:-auto-detect}"
fi

yaml_filename=""
if [[ "${RECORD_VALUE}" == "camerarc" ]]; then
  yaml_filename="cam0_sensor.yaml"
elif [[ "${RECORD_VALUE}" == "camerarl" ]]; then
  yaml_filename="cam1_sensor.yaml"
elif [[ "${RECORD_VALUE}" == "camerarr" ]]; then
  yaml_filename="cam2_sensor.yaml"
fi

if [[ -n "${SIDE}" && -n "${yaml_filename}" ]]; then
  yaml_filename="${SIDE}_${yaml_filename}"
fi

if [[ -n "${yaml_filename}" ]]; then
  export CALIB_YAML_FILENAME="${yaml_filename}"
  echo "Will write YAML: ${yaml_filename}"
else
  unset CALIB_YAML_FILENAME || true
fi

echo "Command: ${RECORD_VALUE}, device: ${SIDE:-single}, serial: ${SERIAL_PORT:-auto-detect}"

CMD=(ros2 run robot_driver camera_calib_cmd "${RECORD_VALUE}")
if [[ -n "${SIDE}" ]]; then
  CMD+=(--side "${SIDE}")
fi
if [[ -n "${SERIAL_PORT}" ]]; then
  CMD+=(--serial-port "${SERIAL_PORT}")
fi

exec "${CMD[@]}"
