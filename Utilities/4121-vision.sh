#!/bin/sh

#   This script enables the FRC Team 4121 Vision processing to start upon boot of the Raspberry Pi 4.
#   Install this script by issuing these commands:
#     sudo cp 4121-vision.sh /etc/init.d
#     cd /etc/rc5.d
#     sudo ln -s ../init.d/4121-vision.sh S024121-vision
#     sudo ln -s ../init.d/4121-vision.sh K024121-vision

. /lib/lsb/init-functions

PIDFILE="/var/run/4121-vision.pid"

if [ "$TEAM4121HOME" = "" ]; then
  TEAM4121HOME="/home/team4121/4121-Vision"
fi
export TEAM4121HOME

if [ "$TEAM4121CONFIG" = "" ]; then
  TEAM4121CONFIG="2024_competition"
fi
export TEAM4121CONFIG

if [ "$TEAM4121VISIONTEST" = "" ]; then
  TEAM4121VISIONTEST="False"
fi
export TEAM4121VISIONTEST

if [ "$NT_SERVER_ADDR" = "" ]; then
  NT_SERVER_ADDR="10.41.21.2"
fi
export NT_SERVER_ADDR

STATUS=0

case "$1" in
  start)
    start-stop-daemon --start --pidfile $PIDFILE --make-pidfile --background --exec ${TEAM4121HOME}/run/raspberrypi4.py
	  STATUS=$?
	  if [ $STATUS != 0 ]; then
	    log_end_msg $STATUS
    fi
    ;;
  stop)
    start-stop-daemon --stop --pidfile $PIDFILE --remove-pidfile --oknodo
	  STATUS=$?
	  if [ $STATUS != 0 ]; then
	    log_end_msg $STATUS
    fi
    ;;
  *)
    echo "Usage: $0 start" >&2
    exit 3
    ;;
esac
exit $STATUS
