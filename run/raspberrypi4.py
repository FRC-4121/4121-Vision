#!/usr/bin/env python3

#System imports
import sys
import os

team4121home = os.environ.get("TEAM4121HOME")
if None == team4121home:
    team4121home = os.getcwd()

team4121config = os.environ.get("TEAM4121CONFIG")
if None == team4121config:
    team4121config = '2024'

#Setup paths
sys.path.append(team4121home + '/lib')

#sys.path.append('C:\\Users\\timfu\\Documents\\Team4121\\Libraries')

#Module imports
import datetime
import time
import logging
import cv2 as cv
from os import getenv
import ntcore
from typing import *
import numpy as np

#Team 4121 module imports
from camera.single import FRCWebCam
from vision.glob._2024 import *

#Set up basic logging
logging.basicConfig(level=logging.DEBUG)

#Declare global variables
cameraFile = team4121home + '/config/' + team4121config + '/CameraSettings.txt'
visionFile = team4121home + '/config/' + team4121config + '/VisionSettings.txt'
cameraValues = {}

#Define program control flags
videoTesting = True
resizeVideo = False
saveVideo = False
networkTablesConnected = True
startupSleep = 0

if getenv("DISPLAY") is None: # We're on the robot, do stuff for realsies
    videoTesting = False

currentTime = time.localtime(time.time())
timeString = "{}-{}-{}_{}:{}:{}".format(currentTime.tm_year, currentTime.tm_mon, currentTime.tm_mday, currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec)

nt = ntcore.NetworkTableInstance.getDefault()

def unwrap_or(val, default):
    if val is None:
        return default
    else:
        return val

visionTable = None
fieldFrame = None
done = 0

def handle_field_objects(frame: np.ndarray, rings: List[FoundObject], tags: List[FoundObject]):
    global done, fieldFrame

    if videoTesting:
        for ring in rings:
            cv.rectangle(frame, (ring.x, ring.y), ((ring.x + ring.w), (ring.y + ring.h)), (0, 0, 255), 2)
            cv.putText(frame, "D: {:6.2f}".format(ring.distance), (ring.x + 10, ring.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "A: {:6.2f}".format(ring.angle), (ring.x + 10, ring.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "O: {:6.2f}".format(ring.offset), (ring.x + 10, ring.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        for tag in tags:
            cv.rectangle(frame, (tag.x, tag.y), ((tag.x + tag.w), (tag.y + tag.h)), (255, 0, 255), 2)
            cv.putText(frame, "D: {:6.2f}".format(tag.distance), (tag.x + 10, tag.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "A: {:6.2f}".format(tag.angle), (tag.x + 10, tag.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "O: {:6.2f}".format(tag.offset), (tag.x + 10, tag.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "I: {:6.2f}".format(tag.ident), (tag.x + 10, tag.y + 60), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            
    
    fieldFrame = frame

    if networkTablesConnected:
        visionTable.putNumber("RingsFound", len(rings))

        for i in range(len(rings)):
            visionTable.putNumber(f"Rings.{i}.distance", unwrap_or(rings[i].distance, -9999.))
            visionTable.putNumber(f"Rings.{i}.angle", unwrap_or(rings[i].angle, -9999.))
            visionTable.putNumber(f"Rings.{i}.offset", unwrap_or(rings[i].offset, -9999.))

        visionTable.putNumber("TagsFound", len(tags))
        for i in range(len(tags)):
            visionTable.putNumber(f"Tags.{i}.distance", unwrap_or(tags[i].distance, -9999.))
            visionTable.putNumber(f"Tags.{i}.angle", unwrap_or(tags[i].angle, -9999.))
            visionTable.putNumber(f"Tags.{i}.offset", unwrap_or(tags[i].offset, -9999.))
            visionTable.putNumber(f"Tags.{i}.id", unwrap_or(tags[i].ident, -9999.))
    
    done += 1

# Define main processing function
def main():

    global timeString, networkTablesConnected, visionTable, done

    time.sleep(startupSleep)


    #Define objects
    visionTable = None
    FRCWebCam.read_config_file(cameraFile)
    fieldCam = FRCWebCam('FIELD', timeString, videofile="FIELD_" + timeString, csname="field")
    VisionBase.read_vision_file(visionFile)

    ringLib = RingVisionLibrary()
    tagLib = AprilTagVisionLibrary()
    
    
    #Open a log file
    logFilename = team4121home + '/logs/run/log_' + timeString + '.txt'
    with open(logFilename, 'w') as log_file:
        log_file.write('run started on {}.\n'.format(datetime.datetime.now()))
        log_file.write('')

        #Connect NetworkTables
        try:
            if networkTablesConnected:
                nt.startClient3("pi4")
                nt.setServer("10.41.21.2")
                visionTable = nt.getTable("vision")
                networkTablesConnected = True
                log_file.write('Connected to Networktables on 10.41.21.2 \n')

                visionTable.putNumber("RobotStop", 0)
                
                timeString = visionTable.getString("Time", timeString)
        except:
            log_file.write('Error:  Unable to connect to Network tables.\n')
            log_file.write('Error message: ', sys.exc_info()[0])
            log_file.write('\n')

        log_file.write("connected to table\n" if networkTablesConnected else "Failed to connect to table\n")
        stop = False
        #Start main processing loop
        while not stop:
            
            ###################
            # Process Web Cam #
            ###################
            done = 0

            fieldThread = fieldCam.use_libs_async(ringLib, tagLib, callback=handle_field_objects)
            
            for i in range(200):
                time.sleep(0.005)
                if done == 1:
                    break
            else:
                if fieldThread.is_alive():
                    print("Field thread is alive for more than one second!")
                    log_file.write("Field thread is alive for more than one second!\n")
                    fieldThread.kill()
            
            if videoTesting:
                cv.imshow("Field", fieldFrame)

            #################################
            # Check for stopping conditions #
            #################################

            #Check for stop code from keyboard (for testing)
            if cv.waitKey(1) == 27:
                break

            #Check for stop code from network tables
            if networkTablesConnected: 
                robotStop = visionTable.getNumber("RobotStop", 0)
                if robotStop == 1 or not networkTablesConnected:
                    break
            

        #Close all open windows (for testing)
        if videoTesting:
            cv.destroyAllWindows()

        #Close the log file
        log_file.write('Run stopped on {}.'.format(datetime.datetime.now()))

if __name__ == "__main__":
    main()
