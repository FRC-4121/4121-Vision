from camera.base import CameraBase
from typing import *
from picamera2 import Picamera2
import numpy as np
import cv2 as cv

# NOTE: the `picamera` library doesn't work on 64-bit targets, despite it being recommended in all of the RPi docs
# `picamera2` is used instead (installed from pip)

Picamera2.set_logging(Picamera2.WARNING)

# Use a picam
class PiCam(CameraBase):
    def __init__(
        self,
        name: str,
        timestamp: str,
        videofile: Optional[str] = None,
        csname: Optional[str] = None,
        profile: bool = False,
    ):
        super().__init__(name, timestamp, videofile, csname, profile)
        self.camStream = Picamera2(int(self.get_config("ID", 0)))
        self.camStream.resolution = (self.width, self.height)
        self.camStream.framerate = self.fps
        self.camStream.brightness = float(self.get_config("BRIGHTNESS", 50))
        self.camStream.start()

    def read_frame_raw(self) -> (bool, np.ndarray):
        self.frame = cv.cvtColor(self.camStream.capture_array(), cv.COLOR_BGR2RGB)
        return True, self.frame

CameraBase.types["PI"] = PiCam
