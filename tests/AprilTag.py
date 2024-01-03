import apriltag
import cv2
import time

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_BRIGHTNESS, 50)  # Brightness
camera.set(cv2.CAP_PROP_EXPOSURE, 100)  # Exposure
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

options = apriltag.DetectorOptions(families="tag36h11")
detector = apriltag.Detector(options)
lastGrabbed = True

height = cv2.getTextSize("0", cv2.FONT_HERSHEY_SIMPLEX, 0.25, 1)[0][1] + 2

while True:
    
    grabbed, frame = camera.read()

    if not grabbed:
        if lastGrabbed:
            print("Failed to grab frame")
            lastGrabbed = False
        # continue

    lastGrabbed = True

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = detector.detect(gray)

    for r in results:
        (ptA, ptB, ptC, ptD) = r.corners
        ptB = (int(ptB[0]), int(ptB[1]))
        ptC = (int(ptC[0]), int(ptC[1]))
        ptD = (int(ptD[0]), int(ptD[1]))
        ptA = (int(ptA[0]), int(ptA[1]))
        # draw the bounding box of the AprilTag detection
        cv2.line(frame, ptA, ptB, (0, 255, 0), 2)
        cv2.line(frame, ptB, ptC, (0, 255, 0), 2)
        cv2.line(frame, ptC, ptD, (0, 255, 0), 2)
        cv2.line(frame, ptD, ptA, (0, 255, 0), 2)

        # draw the tag family on the image
        cv2.putText(frame, str(r.tag_id), (ptA[0], ptA[1] - 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        pose = detector.detection_pose(r, (8.25, 8.25, 320, 240), 0.16)[0]

        cv2.putText(frame, "{: >4.2} {: >4.2} {: >4.2}".format(*pose[0]), (ptB[0] + 15, ptB[1]),
            cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)

        cv2.putText(frame, "{: >4.2} {: >4.2} {: >4.2}".format(*pose[1]), (ptB[0] + 15, ptB[1] + height),
            cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)

        cv2.putText(frame, "{: >4.2} {: >4.2} {: >4.2}".format(*pose[2]), (ptB[0] + 15, ptB[1] + height * 2),
            cv2.FONT_HERSHEY_SIMPLEX, 0.25, (255, 0, 0), 1)

    cv2.imshow("Tags", frame)

    if cv2.waitKey(1) == 27:
        cv2.destroyAllWindows()
        break