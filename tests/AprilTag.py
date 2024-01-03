import pyapriltags
import cv2
import time
import numpy as np
from threading import Thread
import os


params = (8.25, 8.25, 320, 240)
tag_size = 0.16

frames = []
kill = False

def find_cams(port: int):
    file = f"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.{port}/1-1.{port}:1.0/video4linux"
    if os.path.exists(file):
        files = [int(x[5:]) for x in os.listdir(file) if x[:5] == "video" and x[5:].isnumeric()]
        files.sort()
        if len(files) > 0:
            return files[0]

class Runner:
    def __init__(self, idx, port=None, *, id=None):
        self.idx = idx
        self.port = port
        self.id = id if id is not None else find_cams(port)
        self.detector = pyapriltags.Detector(families="tag36h11")
        self.camera = cv2.VideoCapture(self.id)
        self.camera.set(cv2.CAP_PROP_BRIGHTNESS, 50)  # Brightness
        self.camera.set(cv2.CAP_PROP_EXPOSURE, 100)  # Exposure
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.lastGrabbed = True
        self.lastTime = time.monotonic()
        self.frame = np.zeros((480, 620, 3), dtype=np.uint8)
        
        
    def tick(self):
        print(f"tick for {self.id}")
        grabbed, frame = self.camera.read()
        
        if not grabbed:
            if self.lastGrabbed:
                print("Failed to grab frame")
                self.lastGrabbed = False

        self.lastGrabbed = True

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = self.detector.detect(gray, True, params, tag_size)

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

            cv2.putText(frame, "{: >4.2f} {: >4.2f} {: >4.2f}".format(*r.pose_t.flatten()), (ptB[0] + 15, ptB[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 0, 255), 1)


        current = time.monotonic()
        cv2.putText(frame, str(1 // (current - self.lastTime)) + " FPS", (0, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        self.lastTime = current

        self.frame = frame
    
    def launch(self):
        while not kill:
            self.tick()

    def show(self):
        cv2.imshow("Camera " + str(self.port if self.port is not None else self.id), self.frame)

cams = [0, 2]


runners = [Runner(idx, id=port) for (idx, port) in enumerate(cams)]

def run_multi():
    threads = [Thread(target=Runner.launch, name="camera" + str(this.port), args=(this,)) for this in runners]

    for thread in threads:
        thread.start()

    while True:
        for cam in runners:
            cam.show()
        
        if cv2.waitKey(10) == 27:
            cv2.destroyAllWindows()
            kill = True
            break

def run_single():
    while True:
        print("main tick")
        for cam in runners:
            cam.tick()
            cam.show()
        
        if cv2.waitKey(1) == 27:
            cv2.destroyAllWindows()
            kill = True
            break
        print("end")

run_single()