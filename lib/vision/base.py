##################################################################
#                                                                #
#                   FRC Vision Library Base                      #
#                                                                #
#  This class is a base class for all FRC game specific vision   #
#  libraries.  The base class provides methods which are common  #
#  to all game object identification tasks.                      #
#                                                                #
#  @Version: 1.0                                                 #
#  @Created: 2023-1-29                                            #
#  @Author: Team 4121                                            #
#                                                                #
##################################################################

'''FRC Vision Base Class - Provides common vision processing for game elements'''

import cv2 as cv
import numpy as np
import math
from threading import Thread
from typing import *



class FoundObject:

    # initialize FoundObject, with unused fields defaulting to None
    # ty, x, and y are mandatory
    # all other parameters must be named
    def __init__(self, ty, x: int, y: int, *, w: Optional[int] = None, h: Optional[int] = None, radius: Optional[float] = None, distance: Optional[float] = None, angle: Optional[float] = None, offset: Optional[int] = None, percent: Optional[int] = None, ident: Optional[int] = None):
        self.ty = ty
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.radius = radius
        self.distance = distance
        self.angle = angle
        self.offset = offset
        self.percent = percent
        self.ident = ident

    # pretty printing
    def __str__(self):
        out = "found {}".format(self.ty)
        out += "\n    location: ({}, {})".format(self.x, self.y)
        if self.radius is not None:
            out += "\n    radius: {}".format(self.radius)
        if self.distance is not None:
            out += "\n    distance: {}".format(self.distance)
        if self.angle is not None:
            out += "\n    angle: {}".format(self.angle)
        if self.offset is not None:
            out += "\n    offset: {}".format(self.offset)
        if self.percent is not None:
            out += "\n    % of screen: {}".format(self.percent)
        if self.ident is not None:
            out += "\n    id: {}".format(self.ident)
        return out


# Define the class
class VisionBase:

    # Define class fields
    config = {}
    warned = set()
    init = False

    # Class Initialization method
    # Reads the contents of the supplied vision settings file
    def __init__(self):
        
        self.data = []
        self.isFinished = 0


    # Read vision settings file
    @staticmethod
    def read_vision_file(file: str, reload: bool = False) -> bool:
        if VisionBase.init and not reload:
            return True
        VisionBase.init = True
        # Declare local variables
        value_section = ''
        # Open the file and read contents
        try:
            
            # Open the file for reading
            in_file = open(file, 'r')
            
            # Read in all lines
            value_list = in_file.readlines()
            
            # Process list of lines
            for line in value_list:
                
                # Remove trailing newlines and whitespace
                clean_line = line.strip()
                if len(clean_line) == 0:
                    continue
                if clean_line[0] == '#':
                    continue
                # Split the line into parts
                split_line = clean_line.split('=')
                # Determine section of the file we are in
                upper_line = split_line[0].upper()
                
                if upper_line[-1] == ':':
                    value_section = upper_line[:-1]
                    if not value_section in VisionBase.config:
                        VisionBase.config[value_section] = {}
                elif split_line[0] == '':
                    value_section = ''
                    if not value_section in VisionBase.config:
                        VisionBase.config[value_section] = {}
                else:
                    VisionBase.config[value_section][split_line[0].upper()] = split_line[1]
        
        except FileNotFoundError:
            return False
        
        return True

    def cfg(self, name: str, default = None, datatype = str, warn: bool = True):
        c = VisionBase.config[self.name]
        if name in c:
            return datatype(c[name])
        else:
            if warn and not (self.name, name) in VisionBase.warned:
                VisionBase.warned.add((self.name, name))
                print("No parameter {} available for {}!".format(name, self.name))
            return default
        
    # Define basic image processing method for finding contours
    # Converts image from BGR color space to HSV and then applies a mask
    # based on "learned" HSV values from the config file.
    # Edge detection can also be imployed before contours are found and returned.
    def process_image_contours(self, imgRaw: np.ndarray, hsvMin: int, hsvMax: int, erodeDilate: bool, useCanny: bool) -> List[Any]:
        
        finalImg = ""

        # Blur image to remove noise
        blur = cv.GaussianBlur(imgRaw, (13, 13), 0)
        
        # Convert from BGR to HSV colorspace
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

        # Set pixels to white if in target HSV range, else set to black
        mask = cv.inRange(hsv, hsvMin, hsvMax)

        # Detect edges
        if useCanny == True:
            edges = cv.Canny(mask, 35, 125)
        else:
            edges = mask

        if erodeDilate:
            # Erode image to reduce background noise
            kernel = np.ones((3, 3), np.uint8)
            erode = cv.erode(edges, kernel, iterations=2)
            
            # cv.imshow('erode', erode)
            
            # Dilate image to sharpen actual objects
            dilate = cv.dilate(erode, kernel, iterations=2)
            
            # cv.imshow('dilate', dilate)
            
            finalImg = dilate

        else:
            finalImg = edges
        
        # Find contours in mask
        contours, _ = cv.findContours(finalImg, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        
        return list(contours)


    def __str__(self):
        return self.name

    # Define basic image processing method for edge detection
    def process_image_edges(self, imgRaw: np.ndarray):

        # Blur image to remove noise
        blur = cv.GaussianBlur(imgRaw, (13, 13), 0)
        
        # Convert from BGR to HSV colorspace
        hsv = cv.cvtColor(blur, cv.COLOR_BGR2HSV)

        # Detect edges
        edges = cv.Canny(hsv, 35, 125)

        # Find contours using edges
        _, contours, _ = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        return contours
    

    # Method for finding game objects
    # Generic method which will be overidden by child classes
    def find_objects(self, imgRaw: np.ndarray, cameraWidth: int, cameraHeight: int, cameraFOV: int) -> List[FoundObject]:

        return []

    # Update self, storing result. Not meant to be called directly
    def _update(self, imgRaw, cameraWidth, cameraHeight, cameraFOV):

        self.data = self.find_objects(imgRaw, cameraWidth, cameraHeight, cameraFOV)
        self.isFinished = False

    # Start running self in another thread
    def find_objects_threaded(self, imgRaw: np.ndarray, cameraWidth: int, cameraHeight: int, cameraFOV: int, name: str = "findThread"):

        self.isFinished = True

        calcThread = Thread(target=self._update, name=name, args=(imgRaw, cameraWidth, cameraHeight, cameraFOV))
        calcThread.daemon = True
        calcThread.start()

        return self


