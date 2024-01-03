#System imports
import sys

#Setup paths
sys.path.append('lib')

#sys.path.append('C:\\Users\\timfu\\Documents\\Team4121\\Libraries')

#Module imports
import datetime
import time
import logging
import cv2 as cv
from os import getenv
import ntcore

#Team 4121 module imports
from camera.single import FRCWebCam
from vision.glob._2024 import *

#Set up basic logging
logging.basicConfig(level=logging.DEBUG)

#Declare global variables
cameraFile = 'config/2024/CameraSettings.txt'
visionFile = 'config/2024/VisionSettings.txt'
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

def handle_field_objects(frame, rings):
    global done, fieldFrame

    for ring in rings:
        cv.rectangle(frame, (ring.x, ring.y), ((ring.x + ring.w), (ring.y + ring.h)), (0, 0, 255), 2)
        cv.putText(frame, "D: {:6.2f}".format(ring.distance), (ring.x + 10, ring.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        cv.putText(frame, "A: {:6.2f}".format(ring.angle), (ring.x + 10, ring.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        cv.putText(frame, "O: {:6.2f}".format(ring.offset), (ring.x + 10, ring.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
    
    fieldFrame = frame

    if networkTablesConnected:
        visionTable.putNumber("RingsFound", len(rings))

        for i in range(len(rings)):
            visionTable.putNumber("Rings.0.distance", unwrap_or(rings[i].distance, -9999.))
            visionTable.putNumber("Rings.0.angle", unwrap_or(rings[i].angle, -9999.))
            visionTable.putNumber("Rings.0.offset", unwrap_or(rings[i].offset, -9999.))
    
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
    
    
    #Open a log file
    logFilename = 'logs/run/log_' + timeString + '.txt'
    with open(logFilename, 'w') as log_file:
        log_file.write('run started on {}.\n'.format(datetime.datetime.now()))
        log_file.write('')

        #Connect NetworkTables
        try:
            if networkTablesConnected:
                nt.startClient3("pi4")
                nt.setServer("10.41.21.2")
                visionTable = nt.getTable("vision")
                navxTable = nt.getTable("navx")
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

            fieldCam.use_libs_async(ringLib, callback=handle_field_objects)
            
            while done < 1:
                time.sleep(0.005)
            
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
