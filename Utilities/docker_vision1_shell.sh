#!/bin/bash

set -e

docker run -v $PWD:/home/${USER} -v /dev/v4l:/dev/v4l --detach-keys='ctrl-[,z' -it --rm --network host --device=/dev/video0 --device=/dev/video1 team4121-vision-${USER}:00.02 /bin/bash
