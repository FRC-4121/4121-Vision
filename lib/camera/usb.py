from camera.base import *
from typing import *
import os
import cv2 as cv
import numpy as np
import subprocess
import re


# How does this work? I have no idea!
def find_cams(port: int):
    port = int(port)
    port4 = [2, 1, 4, 3][port]
    # Pi 4
    file = f"/sys/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.{port4}/1-1.{port4}:1.0/video4linux"
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
    port5 = [0, 1, 3, 2][port]
    file = "/sys/devices/platform/axi/1000120000.pcie/1f00{0}00000.usb/xhci-hcd.{1}/usb{2}/{2}-{3}/{2}-{3}:1.0/video4linux".format(
        port5 % 2 + 2, port5 % 2, port5 % 2 * 2 + 1, port5 // 2 + 1
    )
    if os.path.exists(file):
        files = [
            int(x[5:])
            for x in os.listdir(file)
            if x[:5] == "video" and x[5:].isnumeric()
        ]
        files.sort()
        if len(files) > 0:
            return files[0]


pi4_re = re.compile(
    "/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.(\\d)/1-1.\\1:1.0.*"
)
pi5_re = re.compile(
    "/devices/platform/axi/1000120000.pcie/1f00(\\d)00000.usb/xhci-hcd.(\\d)/usb(\\d)/\\3-(\\d)/\\3-\\4:1.0.*"
)


# Camera using `cv.VideoCapture`, best for USB camera
class UsbCamera(CameraBase):
    def __init__(
        self, name: str, timestamp: str, params: CameraParams = CameraParams()
    ):
        self.name = name
        port = self.get_config("PORT", None)
        if port is not None:
            port = find_cams(port)
        if port is None:
            self.device_id = self.get_config("ID", None)
            self.device_id = (
                int(self.device_id)
                if self.device_id is not None and self.device_id.isnumeric()
                else self.device_id
            )
        else:
            self.device_id = port

        super().__init__(name, timestamp, params)

        if self.device_id is None:
            self.log_file.write("Can't find camera, either by PORT or ID!\n")
            self.log_file.flush()
            self.evenTry = False
            self.camStream = None
            return

        # setting CAP_PROP_EXPOSURE with OpenCV might work? Seems to only work when inconvenient
        res = subprocess.run(
            [
                "v4l2-ctl",
                "-d",
                f"/dev/video{self.device_id}",
                "-c",
                "auto_exposure=1",
                "-c",
                "exposure_time_absolute=300",
            ]
        )
        self.log_file.write(f"v4l2-ctl configured camera, exit code {res.returncode}\n")

        self.camStream = cv.VideoCapture(self.device_id)
        self.camStream.setExceptionMode(True)
        try:
            if not self.camStream.isOpened():
                self.camStream.open(self.device_id)
            self.evenTry = self.camStream.isOpened()
            if not self.evenTry:
                return
            self.camStream.set(cv.CAP_PROP_FRAME_WIDTH, self.width)
            self.camStream.set(cv.CAP_PROP_FRAME_HEIGHT, self.height)
            self.camStream.set(
                cv.CAP_PROP_BRIGHTNESS, float(self.get_config("BRIGHTNESS", 50))
            )
            try:
                # pass
                self.camStream.set(cv.CAP_PROP_AUTO_EXPOSURE, 1)
                # self.camStream.set(
                #     cv.CAP_PROP_EXPOSURE, float(self.get_config("EXPOSURE", 100))
                # )
            except cv.error as e:
                self.log_file.write(f"Error setting camera exposure: {e}\n")
            self.camStream.set(cv.CAP_PROP_FPS, 1)
            self.camStream.set(cv.CAP_PROP_FOURCC, cv.VideoWriter.fourcc(*"YUYV"))
        except cv.error as e:
            self.log_file.write(f"Error during camera initialization: {e}\n")
            self.evenTry = False

    # Get the name of a camera from its device path
    @staticmethod
    def name_from_devpath(path: str) -> Optional[str]:
        port = None
        if m := pi4_re.fullmatch(path):
            n = int(m.group(1))
            port = [None, 1, 0, 3, 2][n]
        elif m := pi5_re.fullmatch(path):
            n1 = int(m.group(1))
            n2 = int(m.group(2))
            n3 = int(m.group(3))
            n4 = int(m.group(4))
            if n1 - 2 == n2 and n2 * 2 + 1 == n3:
                n = (n2 << 1) | (n4 * 2 - 2)
                port = [0, 1, 3, 2][n]

        if port is not None:
            for name, cfg in CameraBase.config.items():
                if name == "":
                    continue
                if "PORT" in cfg:
                    p = cfg["PORT"]
                    if p.isdigit() and int(p) == port:
                        return name

        for name, cfg in CameraBase.config.items():
            if name == "":
                continue
            if "DEVPATH" in cfg and re.fullmatch(cfg["DEVPATH"], path):
                return name

    def post_init(self):
        if self.evenTry:
            try:
                self.camStream.set(cv.CAP_PROP_FPS, self.fps)
            except cv.error as e:
                self.log_file.write(f"Error during post-init: {e}\n")

    def read_frame_raw(self) -> (bool, np.ndarray):
        if not self.evenTry:
            return False, np.zeros((0, 0, 3))
        if not self.camStream.isOpened():
            self.evenTry = False
            return False, np.zeros((0, 0, 3))
        try:
            good, frame = self.camStream.read()
        except cv.error as e:
            if self.printException:
                self.printException = False
                self.log_file.write(f"Error reading camera: {e}\n")
            return False, np.zeros((0, 0, 3))
        return good, frame


CameraBase.types["USB"] = UsbCamera
