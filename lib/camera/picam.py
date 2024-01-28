from base import CameraBase
from typing import *
import os
import picamera
import numpy as np
from camera.base import CameraBase

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
        self.camStream = picamera.PiCamera(int(self.get_config("ID", 0)))
        self.camStream.resolution = (self.width, self.height)
        self.camStream.framerate = self.fps
        self.camStream.brightness = float(self.get_config("BRIGHTNESS", 50))
    
    def read_frame_raw(self) -> (bool, np.ndarray):
        self.camStream.capture(self.frame, "bgr")
        return True, self.frame