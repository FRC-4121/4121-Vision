import cv2

cam1 = cv2.VideoCapture(0)
cam2 = cv2.VideoCapture(2)

print("initialized cameras")

g1, f1 = cam1.read()

print("grabbed frame 1")

if g1:
    cv2.imshow("Camera 1", f1)
    print("showed frame 1")
else:
    print("skipping grame 1")

g2, f2 = cam2.read()

print("grabbed frame 2")

if g2:
    cv2.imshow("Camera 2", f2)
    print("showed frame 2")
else:
    print("skipping frame 2")

cv2.waitKey(0)
