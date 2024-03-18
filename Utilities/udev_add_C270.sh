#!/bin/dash

#   Critical environment variables for the Team 4121 Vision application:
#       ACTION                  (i.e. "add")
#       DEVPATH                 (i.e. "/devices/platform/axi/1000120000.pcie/1f00300000.usb/xhci-hcd.1/usb3/3-2/3-2:1.0/video4linux/video0")
#       DEVNAME                 (i.e. "/dev/video0")
#       ID_V4L_CAPABILITIES     (i.e. ":capture:" vs ":")
#       ID_PATH_TAG             (i.e. "platform-xhci-hcd_1-usb-0_2_1_0")
#
#       TEAM4121HOME            (i.e. "/home/team4121/4121-Vision")
#       TEAM4121CONFIG          (i.e. "2024_competition")
#       TEAM4121VISIONTEST      (i.e. "False", though in most cases this _should_ default to "False" unless DISPLAY is inadvertently set)
#       TEAM4121VIDEOSAVE       (i.e. "False")
#
#   Optional environment variables:
#       TEAM4121LOGS            (default is $TEAM4121HOME + "/logs")
#       TEAM4121VIDEOS          (default is $TEAM4121HOME + "/videos")
#       TEAM4121CAMERASYNC      (default is "False")
#       NT_SERVER_ADDR          (default is "10.41.21.2")

PIDBASE="/var/run/4121-vision"
LOGBASE="/var/log/4121-vision"

TEAM4121HOME="/home/team4121/4121-Vision"
TEAM4121CONFIG="2024_competition"
TEAM4121VIDEOSAVE="False"
TEAM4121VISIONTEST="False"

export ACTION
export DEVNAME
export DEVPATH
export ID_PATH_TAG
export ID_V4L_CAPABILITIES

export TEAM4121HOME
export TEAM4121CONFIG
export TEAM4121VIDEOSAVE
export TEAM4121VISIONTEST
export TEAM4121LOGS
export TEAM4121VIDEOS
export TEAM4121CAMERASYNC
export NT_SERVER_ADDR

if [ "$ID_V4L_CAPABILITIES" = ":capture:" ]; then
    start-stop-daemon --start --pidfile ${PIDBASE}-${ID_PATH_TAG}.pid --make-pidfile --background --exec ${TEAM4121HOME}/run/raspberrypi4.py
    STATUS=$?
    if [ $STATUS != 0 ]; then
        echo "4121-vision for port" ${ID_PATH_TAG} "FAILED with error" $STATUS >> ${LOGBASE}-${ID_PATH_TAG}.log
    else
        echo "4121-vision for port" ${ID_PATH_TAG} "launched as process" `cat ${PIDBASE}-${ID_PATH_TAG}.pid` >> ${LOGBASE}-${ID_PATH_TAG}.log
    fi
fi
