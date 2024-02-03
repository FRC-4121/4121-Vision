from camera.base import CameraBase
from typing import *
import os
import cv2 as cv
import numpy as np

# How does this work? I have no idea!
def find_cams(port: int):
    port = int(port)
    # Pi 4
    file = f"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.{port}/1-1.{port}:1.0/video4linux"
    if os.path.exists(file):
        files = [
            int(x[5:])
            for x in os.listdir(file)
            if x[:5] == "video" and x[5:].isnumeric()
        ]
        files.sort()
        if len(files) > 0:
            return files[0]
    # Pi 5
    file = "/sys/devices/platform/axi/1000120000.pcie/1f00{0}00000.usb/xhci-hcd.{1}/usb{2}/{2}-{3}/{2}-{3}:1.0/video4linux".format(port % 2 + 2, port % 2, port % 2 * 2 + 1, port // 2 + 1)
    if os.path.exists(file):
        files = [
            int(x[5:])
            for x in os.listdir(file)
            if x[:5] == "video" and x[5:].isnumeric()
        ]
        files.sort()
        if len(files) > 0:
            return files[0]


# Camera using `cv.VideoCapture`, best for USB camera
class UsbCamera(CameraBase):
    def __init__(
        self,
        name: str,
        timestamp: str,
        videofile: Optional[str] = None,
        csname: Optional[str] = None,
        profile: bool = False,
    ):
        self.name = name
        port = self.get_config("PORT", None)
        if port is not None:
            port = find_cams(port)
        if port is None:
            self.device_id = self.get_config("ID", "0")
            self.device_id = (
                int(self.device_id) if self.device_id.isnumeric() else self.device_id
            )
        else:
            self.device_id = port

        super().__init__(name, timestamp, videofile, csname, profile)

        self.camStream = cv.VideoCapture(self.device_id)
        self.camStream.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
        self.camStream.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camStream.set(
            cv.CAP_PROP_BRIGHTNESS, float(self.get_config("BRIGHTNESS", 50))
        )
        self.camStream.set(cv.CAP_PROP_EXPOSURE, int(self.get_config("EXPOSURE", 100)))
        self.camStream.set(cv.CAP_PROP_FPS, 1)
        self.camStream.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc(*"YUYV"))
        self.evenTry = self.camStream.isOpened()

    def post_init(self):
        self.camStream.set(cv.CAP_PROP_FPS, self.fps)

    def read_frame_raw(self) -> (bool, np.ndarray):
        if not self.evenTry:
            return False, np.zeros((0, 0, 3))
        good, frame = self.camStream.read()
        return good, frame


CameraBase.types["USB"] = UsbCamera
