#!/bin/dash

#   Critical environment variables:
#       ACTION                  (i.e. "add")
#       DEVPATH                 (i.e. "/devices/platform/axi/1000120000.pcie/1f00300000.usb/xhci-hcd.1/usb3/3-2/3-2:1.0/video4linux/video0")
#       DEVNAME                 (i.e. "/dev/video0")
#       ID_V4L_CAPABILITIES     (i.e. ":capture:" vs ":")
#       ID_PATH_TAG             (i.e. "platform-xhci-hcd_1-usb-0_2_1_0")

TEAM4121HOME="/home/team4121/4121-Vision"
PIDBASE="/var/run/4121-vision"
LOGBASE="/var/log/4121-vision"

export TEAM4121HOME
export ACTION
export DEVPATH
export DEVNAME
export ID_V4L_CAPABILITIES
export ID_PATH_TAG

if [ "$ID_V4L_CAPABILITIES" = ":capture:" ]; then
    start-stop-daemon --start --pidfile ${PIDBASE}-${ID_PATH_TAG}.pid --make-pidfile --background --exec ${TEAM4121HOME}/run/raspberrypi4.py
    STATUS=$?
    if [ $STATUS != 0 ]; then
        echo "4121-vision for port" ${ID_PATH_TAG} "FAILED with error" $STATUS >> ${LOGBASE}-${ID_PATH_TAG}.log
    else
        echo "4121-vision for port" ${ID_PATH_TAG} "launched as process" `cat ${PIDBASE}-${ID_PATH_TAG}.pid` >> ${LOGBASE}-${ID_PATH_TAG}.log
    fi
fi
