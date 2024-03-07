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
from flush import flush
import time

team4121home = os.getenv("TEAM4121HOME", os.getcwd())
team4121config = os.getenv("TEAM4121CONFIG", "2024")
team4121logs = os.getenv("TEAM4121LOGS", team4121home + "/logs")
team4121videos = os.getenv("TEAM4121VIDEOS", team4121home + "/videos")

killAllThreads = False

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
        csname: str | bool = False,
        profile: bool = False,
        videofile: str | bool = True,
        enabled: bool = True,
    ):
        self.name = name
        self.enabled = enabled
        if not CameraBase.stream:
            csname = False
        if not CameraBase.save:
            videofile = None
        self.profile = profile
        self.name = name

        # Open a log file
        logFilename = "{}/webcam/log_{}_{}.txt".format(
            team4121logs, self.name, timestamp
        )
        linkPath = "{}/webcam/log_{}_LATEST.txt".format(team4121logs, self.name)
        if os.path.exists(linkPath):
            os.unlink(linkPath)
            flush()

        try:
            os.symlink("log_{}_{}.txt".format(self.name, timestamp), linkPath)
        except Exception as e:
            print(e)
            # raise e

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
        self.cropBottom = int(self.get_config("CROP_BOTTOM", 0))

        # Set up video writer
        if type(videofile) is bool:
            if videofile:
                self.videoFilename = "{}/{}_{}.avi".format(team4121videos, name, timestamp)
            else:
                self.videoFilename = None
        else:
            self.videoFilename = videofile

        if self.videoFilename is None:
            self.camWriter = None
            self.saveVideo = False
        else:
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
                self.saveVideo = True
                self.log_file.write("Video writer is open\n")
            else:
                self.saveVideo = False
                self.log_file.write("Video writer is NOT open\n")

        # Initialize blank frames
        self.frame = np.zeros(shape=(self.height, self.width, 3), dtype=np.uint8)

        self.grabbed = True
        self.kill = False

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

        if type(csname) is bool and csname:
            csname = self.get_config("NTNAME", self.name.lower())

        if csname is not False:
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

        pipes = self.get_config("VLIBS", "!")
        if len(pipes) > 0 and pipes[0] == "!":
            self.blacklist = True
            pipes = pipes[1:]
        else:
            self.blacklist = False
        self.pipes = {s.strip() for s in pipes.split(",")}
        self.cameraCounter = 0

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
                    CameraBase.config[value_section][split_line[0].upper()] = (
                        split_line[1]
                    )

        except FileNotFoundError:
            return False

        return True

    @staticmethod
    def init_cam(
        name: str,
        timestamp: str,
        csname: Optional[str] = None,
        videofile: str | bool = True,
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

        return ty(name, timestamp, csname, videofile, profile)

    # Override point for camera
    def read_frame_raw(self) -> (bool, np.ndarray):
        return False, np.zeros((self.width, self.height, 3))

    # Some cameras (currently only USB) need further initalization to run after all of the cameras have been initialized. This method will run this.
    def post_init(self):
        pass

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

    # Grab a frame from the camera, possibly with some preprocessing
    # post_init MUST be called first!
    def read_frame(self) -> np.ndarray:
        # Declare frame for undistorted image
        # newFrame = np.zeros(shape=(self.height, self.width, 3), dtype=np.uint8)

        try:
            # Grab new frame
            self.grabbed, frame = self.read_frame_raw()

            if not self.grabbed:
                return self.frame
            self.frame = frame
            # Undistort image
            if self.undistort_img == True:
                h, w = self.frame.shape[:2]
                new_matrix, roi = cv.getOptimalNewCameraMatrix(
                    self.cam_matrix, self.distort_coeffs, (w, h), 1, (w, h)
                )
                newFrame = cv.undistort(
                    frame, self.cam_matrix, self.distort_coeffs, None, new_matrix
                )
                x, y, w, h = roi
                self.frame = self.frame[y : y + h, x : x + w]
            cv.rectangle(self.frame, (0, self.height - self.cropBottom), (self.width, self.height), (0, 0, 0), -1)
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
                    self.frame,
                    (self.width // self.streamRes, self.height // self.streamRes),
                )
            )
        self.write_video(self.frame)

        # Return the most recent frame
        return self.frame

    # Write a frame to the video file
    def write_video(self, img: np.ndarray):
        # Check if write is opened
        if self.camWriter is not None and self.camWriter.isOpened():
            # Write the image
            try:
                self.camWriter.write(img)
            except Exception as write_error:
                # Print exception info
                self.log_file.write(
                    "Error writing video:\n    type: {}\n    args: {}\n    {}\n".format(
                        type(write_error), write_error.args, write_error
                    )
                )
            if self.cameraCounter < 50:
                self.cameraCounter += 1
            else:
                self.cameraCounter = 0
                self.log_file.flush()
                flush()

    # Release all camera resources
    def close(self):
        # Release video writer
        cw = getattr(self, "camWriter", None)
        if cw is not None:
            cw.release()

        # Close the log file
        self.log_file.write("Webcam closed. Video writer closed.\n")
        self.log_file.close()

    # Apply vision processors to a single frame
    def use_libs(self, *libs, sleep_if_fail: float = 0.0) -> Tuple[np.ndarray, dict]:
        if self.enabled:
            frame = self.read_frame()
            if self.grabbed:
                return (
                    frame,
                    {
                        lib.name: lib.find_objects(
                            frame, self.width, self.height, self.fov
                        )
                        for lib in libs
                        if (lib.name in self.pipes) != self.blacklist
                    },
                )
        time.sleep(sleep_if_fail)
        return (self.frame, dict())

    def _use_libs_fn(self, callback, *libs):
        args = self.use_libs(*libs)
        if self.grabbed or not self.enabled:
            callback(*args)

    def _loop_libs_fn(self, callback, *libs):
        while not self.kill:
            args = self.use_libs(*libs, sleep_if_fail=0.01)
            if self.grabbed or not self.enabled:
                callback(*args)

    def _loop_libs_fn_profile(self, callback, *libs):
        self._loop_libs_fn(callback, *libs)
        # TODO: make this work with new callback code
        # frame = None

        # def time_find(lib):
        #     start = time.monotonic()
        #     ret = lib.find_objects(frame, self.width, self.height, self.fov)
        #     end = time.monotonic()
        #     return str(end - start), ret

        # with open(f"{team4121home}/logs/{self.name}_profile.csv", "w+") as f:
        #     f.write("total,cam,vision,callback,{}\n".format(",".join(map(str, libs))))
        #     while True:
        #         t0 = time.monotonic()
        #         frame = self.read_frame()
        #         t1 = time.monotonic()
        #         times, objs = tuple(map(list, zip(*map(time_find, libs))))
        #         args = (frame, *objs)
        #         t2 = time.monotonic()
        #         if self.grabbed:
        #             callback(*args)
        #         t3 = time.monotonic()
        #         f.write(
        #             ",".join(
        #                 [str(t3 - t0), str(t1 - t0), str(t2 - t1), str(t3 - t2), *times]
        #             )
        #             + "\n"
        #         )
        #         f.flush()

    # Apply vision processors to a single frame, with a callback.
    # Made to easily switch with `use_libs_async`
    def use_libs_sync(self, *libs, callback=lambda _: None):
        args = self.use_libs(*libs)
        if self.grabbed or not self.enabled:
            return callback(*args)

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
