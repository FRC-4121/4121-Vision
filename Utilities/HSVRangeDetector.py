#!/usr/bin/env python

# USAGE: You need to specify a filter and "only one" image source
#
# (python) range-detector --filter RGB --image /path/to/image.png
# or
# (python) range-detector --filter HSV --webcam

import cv2
import sys
from operator import xor


def callback(value):
    pass


def setup_trackbars(range_filter):
    cv2.namedWindow("Trackbars", 0)

    for i in ["MIN", "MAX"]:
        v = 0 if i == "MIN" else 255

        for j in range_filter:
            cv2.createTrackbar("%s_%s" % (j, i), "Trackbars", v, 255, callback)


def get_trackbar_values(range_filter):
    values = []

    for i in ["MIN", "MAX"]:
        for j in range_filter:
            v = cv2.getTrackbarPos("%s_%s" % (j, i), "Trackbars")
            values.append(v)

    return values


def main():
    range_filter = "HSV"

    camera = cv2.VideoCapture(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    camera.set(10, 100)
    camera.set(15, 0)
    # camera.setResolution(640, 480)

    setup_trackbars(range_filter)

    while True:
        ret, image = camera.read()

        if not ret:
            break

        frame_to_thresh = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values(
            range_filter
        )

        thresh = cv2.inRange(
            frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max)
        )

        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)

        if cv2.waitKey(1) == 27:
            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
