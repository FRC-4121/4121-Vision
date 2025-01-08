import cv2 as cv
import numpy as np
import random
import argparse
from math import sin, cos, pi

thresh1 = 100
thresh2 = 100

hmin = 0
hmax = 255
smin = 0
smax = 255
vmin = 0
vmax = 255

blur = 0
blurThresh = 85
minarea = 1000

dilateRadius = 1
dilateMin = 10
dilateIters = 2

def set_val(name):
    def ret(new):
        globals()[name] = new
    return ret

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--controls", action="store_true")
    parser.add_argument("-s", "--show-steps", action="store_true")
    args = parser.parse_args()
    
    if args.controls:
        cv.namedWindow("Canny", 0)
        cv.createTrackbar("1", "Canny", 100, 500, set_val("thresh1"))
        cv.createTrackbar("2", "Canny", 100, 500, set_val("thresh2"))
    
    cv.namedWindow("Filter", 0)
    cv.createTrackbar("blur", "Filter", 0, 50, set_val("blur"))
    cv.createTrackbar("thresh", "Filter", blurThresh, 255, set_val("blurThresh"))
    cv.createTrackbar("minarea", "Filter", minarea, 1000, set_val("minarea"))
    for channel in "hsv":
        for end in ["min", "max"]:
            cv.createTrackbar(channel + end, "Filter", 255 if end == "max" else 0, 255, set_val(channel + end))

    if args.controls:
        cv.namedWindow("Dilate", 0)
        cv.createTrackbar("radius", "Dilate", dilateRadius, 5, set_val("dilateRadius"))
        cv.createTrackbar("minimum", "Dilate", dilateMin, 255, set_val("dilateMin"))
        cv.createTrackbar("iters", "Dilate", dilateIters, 10, set_val("dilateIters"))

    cam = cv.VideoCapture(0)
    while True:
        ret, img = cam.read()
        if not ret:
            break

        cv.imshow("Original", img)
        edges = cv.Canny(img, thresh1, thresh2)
        if args.show_steps:
            cv.imshow("Edges", edges)

        filtered = cv.inRange(cv.cvtColor(img, cv.COLOR_BGR2HSV), (hmin, smin, vmin), (hmax, smax, vmax))
        if args.show_steps:
            cv.imshow("Filtered", filtered)
        blurred = filtered if blur == 0 else cv.blur(filtered, (blur * 2 + 1, blur * 2 + 1))
        blurred = cv.inRange(blurred, blurThresh, 255)
        if args.show_steps:
            cv.imshow("Blurred", blurred)

        masked_edges = cv.bitwise_and(edges, blurred)
        if args.show_steps:
            cv.imshow("Masked Edges", masked_edges)
        
        new_edges = masked_edges
        if dilateRadius > 0:
            for _ in range(dilateIters):
                new_edges = cv.inRange(cv.blur(new_edges, (dilateRadius * 2 + 1, dilateRadius * 2 + 1)), dilateMin, 255)

        if args.show_steps:
            cv.imshow("Final Edges", new_edges)

        final = np.copy(img)
        contours, hierarchy = cv.findContours(new_edges, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)
        for i in range(len(contours)):
            c = contours[i]
            if len(c) < minarea:
                continue
            try:
                cv.drawContours(final, c, i, (255, 0, 0), 10, cv.LINE_8, hierarchy, 0)
            except Exception as e:
                print(e)
            x, y, w, h = cv.boundingRect(c)
            cv.rectangle(final, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv.imshow("Final", final)

        if cv.waitKey(1) == 27:
            break

if __name__ == "__main__":
    main()
