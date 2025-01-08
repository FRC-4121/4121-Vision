#!/usr/bin/env python

# USAGE: You need to specify a filter and "only one" image source
#
# (python) range-detector --filter RGB --image /path/to/image.png
# or
# (python) range-detector --filter HSV --webcam

import cv2
import sys

cvt = [cv2.COLOR_BGR2RGB, cv2.COLOR_BGR2HSV, cv2.COLOR_BGR2HLS, cv2.COLOR_BGR2XYZ, cv2.COLOR_BGR2YCrCb, cv2.COLOR_BGR2Lab, cv2.COLOR_BGR2Luv]

def callback(value):
    pass


def setup_trackbars():
    cv2.namedWindow("Trackbars")
    cv2.createTrackbar("Mode", "Trackbars", 0, len(cvt) - 1, callback)

    for i in ["min", "max"]:
        v = 0 if i == "min" else 255

        for j in range(1, 4):
            cv2.createTrackbar(i + str(j), "Trackbars", v, 255, callback)


def get_trackbar_values():
    values = [cv2.getTrackbarPos("Mode", "Trackbars")]

    for i in ["min", "max"]:
        for j in range(1, 4):
            v = cv2.getTrackbarPos(i + str(j), "Trackbars")
            values.append(v)

    return values

modes = """
Modes:
0: RGB
1: HSV
2: HLS
3: XYZ
4: YCC
5: Lab
6: Luv
"""

def main():
    print(modes)
    camera = cv2.VideoCapture(int(sys.argv[1]) if len(sys.argv) > 1 else 0)
    camera.set(10, 100)
    camera.set(15, 0)
    # camera.setResolution(640, 480)

    setup_trackbars()

    while True:
        ret, image = camera.read()

        if not ret:
            break


        mode, v1_min, v2_min, v3_min, v1_max, v2_max, v3_max = get_trackbar_values()

        frame_to_thresh = cv2.cvtColor(image, cvt[mode])
        thresh = cv2.inRange(frame_to_thresh, (v1_min, v2_min, v3_min), (v1_max, v2_max, v3_max))

        cv2.imshow("Original", image)
        cv2.imshow("Thresh", thresh)

        if cv2.waitKey(1) == 27:
            break

    camera.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
