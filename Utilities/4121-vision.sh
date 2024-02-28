#!/bin/sh
### BEGIN INIT INFO
# Provides:          4121-vision
# Required-Start:    $local_fs udev
# Required-Stop:     $local_fs
# Default-Start:     3 5
# Default-Stop:      0 1 2 4 6
# Short-Description: Start Team 4121 Robot Vision service
# Description:       Start Team 4121 Robot Vision service at boot time.
### END INIT INFO

#   This script enables the FRC Team 4121 Vision processing to start upon boot of the Raspberry Pi 4.
#   Install this script by issuing these commands:
#     sudo cp 4121-vision.sh /etc/init.d
#     cd /etc/rc5.d
#     sudo ln -s ../init.d/4121-vision.sh S024121-vision
#     sudo ln -s ../init.d/4121-vision.sh K024121-vision
#     cd /etc/rc3.d
#     sudo ln -s ../init.d/4121-vision.sh S024121-vision
#     sudo ln -s ../init.d/4121-vision.sh K024121-vision

. /lib/lsb/init-functions

PIDFILE="/var/run/4121-vision.pid"

if [ "$TEAM4121HOME" = "" ]; then
  TEAM4121HOME="/home/team4121/4121-Vision"
fi
export TEAM4121HOME

if [ "$TEAM4121LOGS" = "" ]; then
  TEAM4121LOGS="/mnt/data/4121-Vision/logs"
fi
export TEAM4121LOGS

if [ "$TEAM4121VIDEOS" = "" ]; then
  TEAM4121VIDEOS="/mnt/data/4121-Vision/videos"
fi
export TEAM4121VIDEOS

if [ "$TEAM4121CONFIG" = "" ]; then
  TEAM4121CONFIG="2024_competition"
fi
export TEAM4121CONFIG

if [ "$TEAM4121VISIONTEST" = "" ]; then
  TEAM4121VISIONTEST="False"
fi
export TEAM4121VISIONTEST

if [ "$TEAM4121CAMERASYNC" = "" ]; then
  TEAM4121CAMERASYNC="False"
fi
export TEAM4121CAMERASYNC

if [ "$TEAM4121VIDEOSAVE" = "" ]; then
  TEAM4121VIDEOSAVE="True"
fi
export TEAM4121VIDEOSAVE

if [ "$NT_SERVER_ADDR" = "" ]; then
  NT_SERVER_ADDR="10.41.21.2"
fi
export NT_SERVER_ADDR

STATUS=0

case "$1" in
  start)
    # Only works with logitech!!!
    for cam in 0 1 2 3; do
      v4l2-ctl -d /dev/video$cam -c auto_exposure=1
      v4l2-ctl -d /dev/video$cam -c exposure_time_absolute=300
    done
    for cam in INTAKE SHOOTER; do
        TEAM4121CAMERALIST=$cam
        export TEAM4121CAMERALIST
        start-stop-daemon --start --pidfile $PIDFILE-$cam --make-pidfile --background --exec ${TEAM4121HOME}/run/raspberrypi4.py
        STATUS=$?
        if [ $STATUS != 0 ]; then
          log_end_msg $STATUS
        fi
    done
    ;;
  stop)
    for cam in INTAKE SHOOTER; do
      start-stop-daemon --stop --pidfile $PIDFILE-$cam --remove-pidfile --oknodo
      STATUS=$?
      if [ $STATUS != 0 ]; then
        log_end_msg $STATUS
      fi
    done
    ;;
  *)
    echo "Usage: $0 start" >&2
    exit 3
    ;;
esac
exit $STATUS
