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
import camera.picam
import camera.usb
from camera.base import CameraBase
from vision.glob._2024 import *

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Declare global variables
cameraFile = team4121home + "/config/" + team4121config + "/CameraSettings.txt"
visionFile = team4121home + "/config/" + team4121config + "/VisionSettings.txt"
cameraValues = {}

# Define program control flags
videoTesting = True
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


visionTable = None
fieldFrame = np.zeros((480, 640, 3))
fieldFrames = 0
done = 0
lastFieldTime = time.monotonic()
stop = False

def handle_field_objects(
    frame: np.ndarray, rings: List[FoundObject], tags: List[FoundObject]
):
    global done, fieldFrame, lastFieldTime, fieldFrames
    fieldTime = time.monotonic()
    fieldFps = 1 / (fieldTime - lastFieldTime)
    lastFieldTime = fieldTime
    if videoTesting:
        cv.putText(
            frame,
            "{:3.1f} FPS".format(fieldFps),
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

    fieldFrame = frame
    if nt.isConnected():
        visionTable.putNumber("FieldFPS", fieldFps)
        visionTable.putNumber("RingsFound", len(rings))

        for i in range(len(rings)):
            visionTable.putNumber(
                f"Rings.{i}.distance", unwrap_or(rings[i].distance, -9999.0)
            )
            visionTable.putNumber(
                f"Rings.{i}.angle", unwrap_or(rings[i].angle, -9999.0)
            )
            visionTable.putNumber(
                f"Rings.{i}.offset", unwrap_or(rings[i].offset, -9999.0)
            )

        visionTable.putNumber("TagsFound", len(tags))
        for i in range(len(tags)):
            visionTable.putNumber(
                f"Tags.{i}.distance", unwrap_or(tags[i].distance, -9999.0)
            )
            visionTable.putNumber(f"Tags.{i}.angle", unwrap_or(tags[i].angle, -9999.0))
            visionTable.putNumber(
                f"Tags.{i}.offset", unwrap_or(tags[i].offset, -9999.0)
            )
            visionTable.putNumber(f"Tags.{i}.id", unwrap_or(tags[i].ident, -9999.0))

    done += 1
    fieldFrames += 1

# Define main processing function
def main():
    global timeString, networkTablesConnected, visionTable, done

    time.sleep(startupSleep)

    # Define objects
    CameraBase.read_config_file(cameraFile)
    fieldCam = CameraBase.init_cam(
        "USB2", timeString, videofile="FIELD_" + timeString, csname="field"
    )
    VisionBase.read_vision_file(visionFile)

    ringLib = RingVisionLibrary()
    tagLib = AprilTagVisionLibrary()
    # ringLib = VisionBase()
    # tagLib = VisionBase()

    # Open a log file
    logFilename = team4121home + "/logs/run/log_" + timeString + ".txt"
    with open(logFilename, "w") as log_file:
        log_file.write("run started on {}.\n".format(datetime.datetime.now()))
        log_file.write("")

        # Connect NetworkTables
        try:
            if networkTablesConnected:
                nt.setServer(nt_server_addr)
                nt.startClient3("pi4")
                visionTable = nt.getTable("vision")
                
                log_file.write("Connected to Networktables on {} \n".format(nt_server_addr))

                visionTable.putNumber("RobotStop", 0)

                timeString = visionTable.getString("Time", timeString)
                
                # networkTablesConnected = nt.isConnected()
        except Exception as e:
            log_file.write("Error:  Unable to connect to Network tables.\n")
            log_file.write("Error message: {}\n".format(e))

        log_file.write(
            "connected to table\n"
            if nt.isConnected()
            else "Failed to connect to table\n"
        )
        
        fieldThread = None
        if not syncCamera:
            fieldCam.profile = False
            fieldThread = fieldCam.launch_libs_loop(
                ringLib, tagLib, callback=handle_field_objects
            )
        start = time.monotonic()
        # Start main processing loop
        while not stop:
            if videoTesting:
                cv.imshow("Field", fieldFrame)

            #################################
            # Check for stopping conditions #
            #################################

            # Check for stop code from keyboard (for testing)
            if videoTesting and cv.waitKey(1) == 27:
                break

            # Check for stop code from network tables
            if nt.isConnected():
                robotStop = visionTable.getNumber("RobotStop", 0)
                if robotStop == 1 or not networkTablesConnected:
                    break

            if syncCamera:
                fieldCam.use_libs_sync(ringLib, tagLib, callback=handle_field_objects)

            if not (syncCamera or videoTesting or networkTablesConnected):
                time.sleep(0.0001)
        end = time.monotonic()
        
        log_file.write("Average field FPS: {}\n".format(fieldFrames / (end - start)))

        # Close all open windows (for testing)
        if videoTesting:
            cv.destroyAllWindows()
        
        if fieldThread is not None:
            fieldThread.kill()

        # Close the log file
        log_file.write("Run stopped on {}.".format(datetime.datetime.now()))


if __name__ == "__main__":
    def stopit(*args):
        global stop
        stop = True
    import signal
    signal.signal(signal.SIGUSR1, stopit)
    signal.signal(signal.SIGINT, stopit)
    main()
