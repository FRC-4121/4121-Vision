#!/bin/bash
for cam in 0 2; do
    v4l2-ctl -d /dev/video$cam -c auto_exposure=1
    v4l2-ctl -d /dev/video$cam -c exposure_time_absolute=250
done
