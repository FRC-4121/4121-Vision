#!/bin/bash
for cam in 0 1 2 3; do
    v4l2-ctl -d /dev/video$cam -c auto_exposure=1 2> /dev/null
    v4l2-ctl -d /dev/video$cam -c exposure_time_absolute=300 2> /dev/null
done
