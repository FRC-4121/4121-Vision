#!/usr/bin/env python3

# System imports
import sys
import os

team4121home = os.environ.get("TEAM4121HOME")
if None == team4121home:
    team4121home = os.getcwd()

team4121config = os.environ.get("TEAM4121CONFIG")
if None == team4121config:
    team4121config = "2024"

team4121visiontest = os.environ.get("TEAM4121VISIONTEST")
if None == team4121visiontest:
    team4121visiontest = "True"

nt_server_addr = os.environ.get("NT_SERVER_ADDR")
if None == nt_server_addr:
    nt_server_addr = "10.41.21.2"

# Setup paths
sys.path.append(team4121home + "/lib")

# sys.path.append('C:\\Users\\timfu\\Documents\\Team4121\\Libraries')

# Module imports
import datetime
import time
import logging
import cv2 as cv
from os import getenv
import ntcore
from typing import *
import numpy as np

# Team 4121 module imports
# import camera.picam
import camera.frame
import camera.usb
from camera.base import CameraBase
from vision.glob._2024 import *
from threads import KillableThread

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Declare global variables
cameraFile = team4121home + "/config/" + team4121config + "/CameraSettings.txt"
visionFile = team4121home + "/config/" + team4121config + "/VisionSettings.txt"
cameraValues = {}

# Define program control flags
if team4121visiontest.lower() in ["true", "1", "t", "y", "yes"]:
    videoTesting = True
else:
    videoTesting = False
resizeVideo = False
saveVideo = False
networkTablesConnected = True
syncCamera = True
startupSleep = 0

if getenv("DISPLAY") is None:  # We're on the robot, do stuff for realsies
    videoTesting = False

currentTime = time.localtime(time.time())
timeString = "{}-{}-{}_{}:{}:{}".format(
    currentTime.tm_year,
    currentTime.tm_mon,
    currentTime.tm_mday,
    currentTime.tm_hour,
    currentTime.tm_min,
    currentTime.tm_sec,
)

nt = ntcore.NetworkTableInstance.getDefault()


def unwrap_or(val, default):
    if val is None:
        return default
    else:
        return val


done = 0
stop = False


class PollerFn:
    def __init__(self, call: Callable[[], Any], maxCount: int = 50):
        self.ret = call()
        self.call = call
        self.count = 0
        self.maxCount = maxCount

    def __call__(self):
        if self.count >= self.maxCount:
            self.ret = self.call()
            self.count = 0
            return self.ret
        self.count += 1
        return self.ret


ntIsConnected = PollerFn(lambda: nt.isConnected())


class CameraCallback:
    def __init__(self, table, cam):
        self.table = table
        self.cam = cam
        self.frame = np.zeros((480, 640, 3))
        self.frames = 0
        self.minFps = 100
        self.maxFps = 0
        self.avgFps = 0
        self.lastTime = time.monotonic()

    def __call__(self, frame: np.ndarray, res: Dict[str, List[FoundObject]]):
        global done
        fieldTime = time.monotonic()
        fieldFps = 1 / (fieldTime - self.lastTime)
        self.lastTime = fieldTime
        self.avgFps *= min(self.frames, 150)
        self.avgFps += fieldFps
        self.avgFps /= min(self.frames, 150) + 1
        if self.frames < 15 and fieldFps < self.minFps:
            self.minFps = fieldFps
        if self.frames < 15 and fieldFps > self.maxFps:
            self.maxFps = fieldFps
        rings = res["RING"] if "RING" in res else []
        tags = res["APRIL"] if "APRIL" in res else []
        if videoTesting:
            cv.putText(
                frame,
                "{:4.1f}/{:4.1f}/{:4.1f}/{:4.1f} FPS".format(
                    fieldFps, self.avgFps, self.minFps, self.maxFps
                ),
                (0, 15),
                cv.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
            for ring in rings:
                cv.rectangle(
                    frame,
                    (ring.x, ring.y),
                    ((ring.x + ring.w), (ring.y + ring.h)),
                    (0, 0, 255),
                    2,
                )
                cv.putText(
                    frame,
                    "D: {:6.2f}".format(ring.distance),
                    (ring.x + 10, ring.y + 15),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 0),
                    1,
                )
                cv.putText(
                    frame,
                    "A: {:6.2f}".format(ring.angle),
                    (ring.x + 10, ring.y + 30),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 0),
                    1,
                )
                cv.putText(
                    frame,
                    "O: {:6.2f}".format(ring.offset),
                    (ring.x + 10, ring.y + 45),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 0, 0),
                    1,
                )
            for tag in tags:
                cv.rectangle(
                    frame,
                    (tag.x, tag.y),
                    ((tag.x + tag.w), (tag.y + tag.h)),
                    (255, 0, 255),
                    2,
                )
                cv.putText(
                    frame,
                    "D: {:6.2f}".format(tag.distance),
                    (tag.x + 10, tag.y + 15),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                )
                cv.putText(
                    frame,
                    "A: {:6.2f}".format(tag.angle),
                    (tag.x + 10, tag.y + 30),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                )
                cv.putText(
                    frame,
                    "O: {:6.2f}".format(tag.offset),
                    (tag.x + 10, tag.y + 45),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                )
                cv.putText(
                    frame,
                    "I: {}".format(tag.ident),
                    (tag.x + 10, tag.y + 60),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.3,
                    (0, 255, 0),
                    1,
                )

        self.frame = frame

        if ntIsConnected():
            self.table.putNumber("FPS", fieldFps)

            self.table.putNumber("RingsFound", len(rings))

            for i in range(len(rings)):
                self.table.putNumber(
                    f"Rings.{i}.distance", unwrap_or(rings[i].distance, -9999.0)
                )
                self.table.putNumber(
                    f"Rings.{i}.angle", unwrap_or(rings[i].angle, -9999.0)
                )
                self.table.putNumber(
                    f"Rings.{i}.offset", unwrap_or(rings[i].offset, -9999.0)
                )

            self.table.putNumber("TagsFound", len(tags))
            for i in range(len(tags)):
                self.table.putNumber(
                    f"Tags.{i}.distance", unwrap_or(tags[i].distance, -9999.0)
                )
                self.table.putNumber(
                    f"Tags.{i}.angle", unwrap_or(tags[i].angle, -9999.0)
                )
                self.table.putNumber(
                    f"Tags.{i}.offset", unwrap_or(tags[i].offset, -9999.0)
                )
                self.table.putNumber(f"Tags.{i}.id", unwrap_or(tags[i].ident, -9999.0))

            self.cam.enabled = self.table.getBoolean("Enabled")

        done += 1
        self.frames += 1


class CameraLoop:
    def __init__(
        self,
        name: str,
        table: ntcore.NetworkTable | str | None = None,
        videofile: str | bool = False,
        csname: str | bool = False,
        profile: bool = False,
    ):
        if type(videofile) is bool:
            if videofile:
                videofile = f"{name}_{timeString}"
            else:
                videofile = None

        self.name = name
        self.cam = CameraBase.init_cam(name, timeString, videofile, csname, profile)

        if table is None:
            table = self.cam.get_config("NTNAME", self.cam.name.lower())

        if type(table) is str:
            table = nt.getTable(table)

        self.callback = CameraCallback(table, self.cam)
        # self.libs = (RingVisionLibrary(), AprilTagVisionLibrary())
        self.libs = [VisionBase()] * 2

    def launch_loop(self) -> KillableThread:
        self.thread = self.cam.launch_libs_loop(*self.libs, callback=self.callback)
        return self.thread

    def cam_tick_sync(self):
        self.cam.use_libs_sync(*self.libs, callback=self.callback)

    def update_video(self):
        cv.imshow(self.name, self.callback.frame)


# Define main processing function
def main():
    global timeString, networkTablesConnected, visionTable, done

    time.sleep(startupSleep)

    # Define objects
    CameraBase.read_config_file(cameraFile)
    VisionBase.read_vision_file(visionFile)

    # Open a log file
    logFilename = team4121home + "/logs/run/log_" + timeString + ".txt"
    linkPath = team4121home + "/logs/run/log_LATEST.txt"
    if os.path.exists(linkPath):
        os.unlink(linkPath)
    os.symlink("log_" + timeString + ".txt", linkPath)
    with open(logFilename, "w") as log_file:
        try:
            log_file.write("Run started on {}.\n".format(datetime.datetime.now()))
            log_file.write("")
            controlTable = None

            # Connect NetworkTables
            try:
                if networkTablesConnected:
                    nt.setServer(nt_server_addr)
                    nt.startClient3("pi4")
                    controlTable = nt.getTable("control")

                    log_file.write(
                        "Connected to Networktables on {} \n".format(nt_server_addr)
                    )

                    controlTable.putNumber("RobotStop", 0)

                    timeString = controlTable.getString("Time", timeString)

                    # networkTablesConnected = ntIsConnected()
            except Exception as e:
                log_file.write("Error:  Unable to connect to Network tables.\n")
                log_file.write("Error message: {}\n".format(e))

            log_file.write(
                "connected to table\n"
                if ntIsConnected()
                else "Failed to connect to table\n"
            )

            def checkStop():
                if ntIsConnected() and controlTable.getNumber("RobotStop", 0) == 1:
                    stop = True

            checkStop = PollerFn(checkStop)
            cams = [CameraLoop("INTAKE"), CameraLoop("SHOOTER")]
            # cams = [CameraLoop("DUMMY")]
            threads = []

            # post-initializer call, this MUST happen
            for cam in cams:
                cam.cam.post_init()

            if not syncCamera:
                threads = [cam.launch_loop() for cam in cams]
            start = time.monotonic()
            # Start main processing loop
            while not stop:
                if videoTesting:
                    for cam in cams:
                        cam.update_video()

                #################################
                # Check for stopping conditions #
                #################################

                # Check for stop code from keyboard (for testing)
                if videoTesting and cv.waitKey(1) == 27:
                    break

                # Check for stop code from network tables
                checkStop()

                if syncCamera:
                    for cam in cams:
                        cam.cam_tick_sync()

                if not (syncCamera or videoTesting or networkTablesConnected):
                    time.sleep(0.0001)
            end = time.monotonic()

            for cam in cams:
                log_file.write(
                    "Average FPS for {}: {:5.2f}/{:5.2f}/{:5.2f}/{:5.2f}\n".format(
                        cam.name,
                        cam.callback.frames / (end - start),
                        cam.callback.avgFps,
                        cam.callback.minFps,
                        cam.callback.maxFps,
                    )
                )

            # Close all open windows (for testing)
            if videoTesting:
                cv.destroyAllWindows()

            for thread in threads:
                thread.kill()

            # Close the log file
            log_file.write("Run stopped on {}.\n".format(datetime.datetime.now()))
        except Exception as e:
            log_file.write(f"An exception occured: {e}\n")


if __name__ == "__main__":

    def stopit(*args):
        global stop
        stop = True

    import signal
    import gc

    signal.signal(signal.SIGUSR1, stopit)
    signal.signal(signal.SIGINT, stopit)

    gc.set_threshold(10000, 100, 100)
    gc.disable()

    main()
