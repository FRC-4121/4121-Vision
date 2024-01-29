######################################################################
#                                                                    #
#                        FRC Camera Library                          #
#                                                                    #
#  This class provides methods and utilities for web cameras used    #
#  for vision processing during an FRC game.  Reading of the webcam  #
#  frames is threaded for improved performance.                      #
#                                                                    #
# @Version: 2.0                                                      #
# @Created: 2020-02-07                                               #
# @Revised: 2021-02-16                                               #
# @Author: Team 4121                                                 #
#                                                                    #
######################################################################
"""FRC Camera Library - Provides threaded camera methods and utilities"""

# System imports
import sys
import os
from typing import *
import cv2 as cv
import numpy as np
import importlib as imp
from threads import KillableThread
import time

CvSource = None
VideoMode = None

cscore_available = False
try:
    loader = imp.find_loader("cscore")
    cscore_available = loader is not None
except ImportError:
    cscore_available = False


def load_cscore():
    global CvSource, VideoMode
    if CvSource is None or VideoMode is None:
        import cscore

        CvSource = cscore.CvSource
        VideoMode = cscore.VideoMode

team4121home = os.environ.get("TEAM4121HOME")
if None == team4121home:
    team4121home = os.getcwd()

team4121config = os.environ.get("TEAM4121CONFIG")
if None == team4121config:
    team4121config = "2024"

# Set global variables
calibration_dir = team4121home + "config" + team4121config


# This is the base camera, from which all of our cameras inherit
# The default initializer should probably be called before the rest of the initializer in derived classes
# In addition, the `init_cam` static method can delegate to a derived class by reading the "TYPE" field in the config
# The derived camera's module must first be loaded
class CameraBase:
    config = {"": {}}
    init = False
    stream = cscore_available
    save = True
    types = {}

    # Define initialization
    def __init__(
        self,
        name: str,
        timestamp: str,
        videofile: Optional[str] = None,
        csname: Optional[str] = None,
        profile: bool = False,
    ):
        if not CameraBase.stream:
            csname = None
        if not CameraBase.save:
            videofile = None
        self.profile = profile
        self.name = name
        

        # Open a log file
        logFilename =  "{}/logs/webcam/log_{}_{}.txt".format(team4121home, self.name, timestamp)
        if videofile is None:
            videofile = "{}_{}".format(name, timestamp)
        self.log_file = open(logFilename, "w")
        self.log_file.write("Initializing webcam: {}\n".format(self.name))
        # Initialize instance variables
        self.undistort_img = False

        # Store frame size
        self.height = int(self.get_config("HEIGHT", 240))
        self.width = int(self.get_config("WIDTH", 320))
        self.fov = float(self.get_config("FOV", 0.0))
        self.fps = int(self.get_config("FPS", 30))
        self.streamRes = int(self.get_config("STREAM_RES", 1))

        # Set up video writer
        self.videoFilename = "videos/" + videofile + ".avi"
        fourcc = cv.VideoWriter_fourcc(*"MJPG")
        self.camWriter = cv.VideoWriter(
            self.videoFilename, fourcc, self.fps, (self.width, self.height)
        )

        try:
            self.camWriter.open(
                self.videoFilename,
                fourcc,
                float(self.fps),
                (self.width, self.height),
                True,
            )
        except Exception as e:
            self.log_file.write(
                "Error opening video writer for {}\n{}\n".format(self.videoFilename, e)
            )

        if self.camWriter.isOpened():
            self.log_file.write("Video writer is open\n")
        else:
            self.log_file.write("Video writer is NOT open\n")

        # Initialize blank frames
        self.frame = np.zeros(shape=(self.height, self.width, 3), dtype=np.uint8)

        self.grabbed = True

        # Name the stream
        self.name = name

        # Initialize stop flag
        self.stopped = False

        # Read camera calibration files
        # cam_matrix_file = (
        #     calibration_dir + "/Camera_Matrix_Cam" + str(self.device_id) + ".txt"
        # )
        # cam_coeffs_file = (
        #     calibration_dir + "/Distortion_Coeffs_Cam" + str(self.device_id) + ".txt"
        # )
        # if (
        #    os.path.isfile(cam_matrix_file) == True
        #    and os.path.isfile(cam_coeffs_file) == True
        # ):
        #    self.cam_matrix = np.loadtxt(cam_matrix_file)
        #    self.distort_coeffs = np.loadtxt(cam_coeffs_file)
        #    self.undistort_img = True

        if csname is not None:
            load_cscore()
            self.cvs = CvSource(
                csname,
                VideoMode.PixelFormat.kBGR,
                self.width // self.streamRes,
                self.height // self.streamRes,
                self.fps,
            )
        else:
            self.cvs = None

        # Log init complete message
        self.log_file.write("Webcam initialization complete\n")

    @staticmethod
    def read_config_file(file, reload: bool = False) -> bool:
        if CameraBase.init and not reload:
            return True
        CameraBase.init = True
        # Declare local variables
        value_section = ""
        # Open the file and read contents
        try:
            # Open the file for reading
            in_file = open(file, "r")

            # Read in all lines
            value_list = in_file.readlines()

            # Process list of lines
            for line in value_list:
                # Remove trailing newlines and whitespace
                clean_line = line.strip()
                if len(clean_line) == 0:
                    continue

                if clean_line[0] == "#":
                    continue
                # Split the line into parts
                split_line = clean_line.split("=")
                # Determine section of the file we are in
                upper_line = split_line[0].upper()

                if upper_line[-1] == ":":
                    value_section = upper_line[:-1]
                    if not value_section in CameraBase.config:
                        CameraBase.config[value_section] = {}
                elif split_line[0] == "":
                    value_section = ""
                    if not value_section in CameraBase.config:
                        CameraBase.config[value_section] = {}
                else:
                    CameraBase.config[value_section][split_line[0].upper()] = split_line[
                        1
                    ]

        except FileNotFoundError:
            return False

        return True
    
    @staticmethod
    def init_cam(
        name: str,
        timestamp: str,
        videofile: Optional[str] = None,
        csname: Optional[str] = None,
        profile: bool = False,
    ):
        ty = None
        
        if name in CameraBase.config:
            cfg = CameraBase.config[name]
            if "TYPE" in cfg:
                ty = CameraBase.types[cfg["TYPE"]]
        if ty is not None:
            cfg = CameraBase.config[""]
            if "TYPE" in cfg:
                ty = CameraBase.types[cfg["TYPE"]]
        if ty is None:
            raise KeyError("camera type not specified!")
        
        return ty(name, timestamp, videofile, csname, profile)

    # Override point for camera
    def read_frame_raw(self) -> (bool, np.ndarray):
        return False, np.zeros((self.width, self.height, 3))

    # Get a camera configuration value
    def get_config(self, name: str, default: str) -> str:
        if self.name in CameraBase.config:
            cfg = CameraBase.config[self.name]
            if name in cfg:
                return cfg[name]
        cfg = CameraBase.config[""]
        if name in cfg:
            return cfg[name]
        return default

    # Run camera updates in another thread
    def start_camera_thread(self):
        self.stopped = False
        camThread = KillableThread(target=self._run_in_thread, name=self.name, args=())
        camThread.daemon = True
        camThread.start()

        return self

    # Send signal to stop
    def stop_camera_thread(self) -> None:
        self.stopped = True

    # Run self in other thread. Not to be called directly
    def _run_in_thread(self) -> None:
        # Main thread loop
        while True:
            # Check stop flag
            if self.stopped:
                return

            # If not stopping, grab new frame
            self.grabbed, self.frame = self.camStream.read()

    # Grab a frame from the camera, possibly with some preprocessing
    def read_frame(self) -> np.ndarray:
        # Declare frame for undistorted image
        newFrame = np.zeros(shape=(self.height, self.width, 3), dtype=np.uint8)

        try:
            # Grab new frame
            self.grabbed, frame = self.read_frame_raw()

            if not self.grabbed:
                return newFrame

            # Undistort image
            if self.undistort_img == True:
                h, w = frame.shape[:2]
                new_matrix, roi = cv.getOptimalNewCameraMatrix(
                    self.cam_matrix, self.distort_coeffs, (w, h), 1, (w, h)
                )
                newFrame = cv.undistort(
                    frame, self.cam_matrix, self.distort_coeffs, None, new_matrix
                )
                x, y, w, h = roi
                newFrame = newFrame[y : y + h, x : x + w]

            else:
                newFrame = frame

        except Exception as read_error:
            # Write error to log
            self.log_file.write(
                "Error reading video:\n    type: {}\n    args: {}\n    {}\n".format(
                    type(read_error), read_error.args, read_error
                )
            )

        if self.cvs is not None:
            self.cvs.putFrame(
                cv.resize(
                    newFrame,
                    (self.width // self.streamRes, self.height // self.streamRes),
                )
            )

        # Return the most recent frame
        return newFrame

    # Write a frame to the video file
    def write_video(self, img: np.ndarray) -> bool:
        # Check if write is opened
        if self.camWriter.isOpened():
            # Write the image
            try:
                self.camWriter.write(img)
                return True

            except Exception as write_error:
                # Print exception info
                self.log_file.write(
                    "Error writing video:\n    type: {}\n    args: {}\n    {}\n".format(
                        type(write_error), write_error.args, write_error
                    )
                )
                return False

        else:
            self.log_file.write("Video writer not opened!\n")
            return False

    # Release all camera resources
    def release_cam(self):
        # Release the camera resource
        self.camStream.release()

        # Release video writer
        self.camWriter.release()

        # Close the log file
        self.log_file.write("Webcam closed. Video writer closed.\n")
        self.log_file.close()

    # Apply vision processors to a single frame
    def use_libs(self, *libs) -> List[Any]:
        frame = self.read_frame()
        return (
            frame,
            *[
                lib.find_objects(frame, self.width, self.height, self.fov)
                for lib in libs
            ],
        )

    def _use_libs_fn(self, callback, *libs):
        callback(*self.use_libs(*libs))

    def _loop_libs_fn(self, callback, *libs):
        while True:
            callback(*self.use_libs(*libs))

    def _loop_libs_fn_profile(self, callback, *libs):
        frame = None

        def time_find(lib):
            start = time.monotonic()
            ret = lib.find_objects(frame, self.width, self.height, self.fov)
            end = time.monotonic()
            return str(end - start), ret

        with open(f"{team4121home}/logs/{self.name}_profile.csv", "w+") as f:
            f.write("total,cam,vision,callback,{}\n".format(",".join(map(str, libs))))
            while True:
                t0 = time.monotonic()
                frame = self.read_frame()
                t1 = time.monotonic()
                times, objs = tuple(map(list, zip(*map(time_find, libs))))
                args = (frame, *objs)
                t2 = time.monotonic()
                callback(*args)
                t3 = time.monotonic()
                f.write(
                    ",".join(
                        [str(t3 - t0), str(t1 - t0), str(t2 - t1), str(t3 - t2), *times]
                    )
                    + "\n"
                )
                f.flush()

    # Apply vision processors to a single frame, with a callback.
    # Made to easily switch with `use_libs_async`
    def use_libs_sync(self, *libs, callback=lambda _: None):
        return callback(*self.use_libs(*libs))

    # Apply vision processors to a single frame, running in another thread
    def use_libs_async(
        self, *libs, callback=lambda _: None, name: str = "vision"
    ) -> KillableThread:
        thread = KillableThread(
            target=self._use_libs_fn, args=(callback, *libs), name=name
        )
        thread.daemon = True
        thread.start()
        return thread

    def launch_libs_loop(
        self, *libs, callback=lambda _: None, name: str = "vision_loop"
    ) -> KillableThread:
        thread = KillableThread(
            target=(self._loop_libs_fn_profile if self.profile else self._loop_libs_fn),
            args=(callback, *libs),
            name=name,
        )
        thread.daemon = True
        thread.start()
        return thread