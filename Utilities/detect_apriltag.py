#!/usr/bin/env python3

# import the necessary packages
import pyapriltags as apriltag
import argparse
import cv2

params = (8.25, 8.25, 320, 240)
tag_size = 0.16

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
group = ap.add_mutually_exclusive_group(required=True)
group.add_argument("-i", "--image", metavar="PATH", help="path to input image containing AprilTag")
group.add_argument("-c", "--cam", metavar="ID", nargs="?", type=int, default=0, help="use camera frame")
args = ap.parse_args()

image = cv2.imread(args) if args.image is not None else cv2.VideoCapture(args.cam if args.cam is not None else 0).read()[1]
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

detector = apriltag.Detector(families="tag36h11")
results = detector.detect(gray, True, params, tag_size)

# loop over the AprilTag detection results
for r in results:
	# extract the bounding box (x, y)-coordinates for the AprilTag
	# and convert each of the (x, y)-coordinate pairs to integers
	(ptA, ptB, ptC, ptD) = r.corners
	ptB = (int(ptB[0]), int(ptB[1]))
	ptC = (int(ptC[0]), int(ptC[1]))
	ptD = (int(ptD[0]), int(ptD[1]))
	ptA = (int(ptA[0]), int(ptA[1]))
	
	# draw the bounding box of the AprilTag detection
	cv2.line(image, ptA, ptB, (0, 255, 0), 2)
	cv2.line(image, ptB, ptC, (0, 255, 0), 2)
	
	cv2.line(image, ptC, ptD, (0, 255, 0), 2)
	cv2.line(image, ptD, ptA, (0, 255, 0), 2)
	
	# draw the center (x, y)-coordinates of the AprilTag
	(cX, cY) = (int(r.center[0]), int(r.center[1]))
	cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)
	
	# draw the tag family on the image
	tagId = r.tag_id
	cv2.putText(image, str(tagId), (ptA[0], ptA[1] - 15),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
	
	
# show the output image after AprilTag detection
cv2.imshow("Image", image)

cv2.waitKey(0)
