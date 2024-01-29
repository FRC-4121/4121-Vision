#!/usr/bin/env python3

import cv2 as cv
import numpy as np
import os
import time

cams = []
for id in range(10):
    cs = cv.VideoCapture(id)
    if cs.isOpened():
        print(id)
        cs.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cs.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        cs.set(cv.CAP_PROP_BRIGHTNESS, 100)
        cs.set(cv.CAP_PROP_EXPOSURE, 0)
        cs.set(cv.CAP_PROP_FPS, 15)
        cams.append((cs, "Camera {}".format(id)))

for id in os.listdir("/dev/v4l/by-path") if os.path.exists("/dev/v4l/by-path") else []:
    cs = cv.VideoCapture(id)
    if cs.isOpened():
        print(id)
        cs.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cs.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        cs.set(cv.CAP_PROP_BRIGHTNESS, 100)
        cs.set(cv.CAP_PROP_EXPOSURE, 0)
        cs.set(cv.CAP_PROP_FPS, 15)
        cams.append((cs, id))

for id in os.listdir("/dev/v4l/by-id") if os.path.exists("/dev/v4l/by-id") else []:
    cs = cv.VideoCapture(id)
    if cs.isOpened():
        print(id)
        cs.set(cv.CAP_PROP_FRAME_WIDTH, 640)
        cs.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
        cs.set(cv.CAP_PROP_BRIGHTNESS, 100)
        cs.set(cv.CAP_PROP_EXPOSURE, 0)
        cs.set(cv.CAP_PROP_FPS, 15)
        cams.append((cs, id))

last = time.monotonic()

if len(cams) > 0:
    while True:
        for cs, name in cams:
            frame = np.zeros(shape=(640, 480, 3), dtype=np.uint8)

            try:
                good, new_frame = cs.read()
                if not good:
                    continue
                frame = new_frame

            except Exception as read_error:
                # Write error to log
                print(
                    "Error reading video:\n    type: {}\n    args: {}\n    {}".format(
                        type(read_error), read_error.args, read_error
                    )
                )

            cv.imshow(name, frame)

        current = time.monotonic()
        print(1 / (current - last), end="\r")
        last = current

        if cv.waitKey(1) == 27:
            cv.destroyAllWindows()
            exit(0)
else:
    print("No cameras found :'(")
