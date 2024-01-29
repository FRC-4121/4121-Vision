from camera.base import CameraBase
from typing import *
import os
import cv2 as cv
import numpy as np


def find_cams(port: int):
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
        self.camStream.set(cv.CAP_PROP_FPS, self.fps)

    def read_frame_raw(self) -> (bool, np.ndarray):
        good, frame = self.camStream.read()
        if not good:
            frame = np.zeros((self.width, self.height, 3))
        return good, frame


CameraBase.types["USB"] = UsbCamera
