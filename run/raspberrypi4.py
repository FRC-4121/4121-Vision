#!/usr/bin/env python3

#System imports
import sys
import os

team4121home = os.environ.get("TEAM4121HOME");
if None == team4121home:
    team4121home = os.getcwd()

team4121config = os.environ.get("TEAM4121CONFIG");
if None == team4121config:
    team4121config = '2023'

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

#Team 4121 module imports
from camera.single import FRCWebCam
from vision.glob._2023 import *

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
done = 0
fieldFrame = None
tapeFrame = None
def handle_field_objects(frame, cubes, cones):
    global done, fieldFrame
    if len(cubes) >= 1:

        cube = cubes[0]
        cv.rectangle(frame, (cube.x, cube.y), ((cube.x + cube.w), (cube.y + cube.h)), (0, 0, 255), 2)
        cv.putText(frame, "D: {:6.2f}".format(cube.distance), (cube.x + 10, cube.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        cv.putText(frame, "A: {:6.2f}".format(cube.angle), (cube.x + 10, cube.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        cv.putText(frame, "O: {:6.2f}".format(cube.offset), (cube.x + 10, cube.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)

        if len(cubes) >= 2:
            cube = cubes[1]
            cv.rectangle(frame, (cube.x, cube.y), ((cube.x + cube.w), (cube.y + cube.h)), (0, 255, 0), 2)
            cv.putText(frame, "D: {:6.2f}".format(cube.distance), (cube.x + 10, cube.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "A: {:6.2f}".format(cube.angle), (cube.x + 10, cube.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "O: {:6.2f}".format(cube.offset), (cube.x + 10, cube.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)

            if len(cubes) >= 3:
                cube = cubes[2]
                cv.rectangle(frame, (cube.x, cube.y), ((cube.x + cube.w), (cube.y + cube.h)), (0, 255, 0), 2)
                cv.putText(frame, "D: {:6.2f}".format(cube.distance), (cube.x + 10, cube.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
                cv.putText(frame, "A: {:6.2f}".format(cube.angle), (cube.x + 10, cube.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
                cv.putText(frame, "O: {:6.2f}".format(cube.offset), (cube.x + 10, cube.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        
    if len(cones) >= 1:

        cone = cones[0]
        cv.rectangle(frame, (cone.x, cone.y), ((cone.x + cone.w), (cone.y + cone.h)), (0, 0, 255), 2)
        cv.putText(frame, "D: {:6.2f}".format(cone.distance), (cone.x + 10, cone.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        cv.putText(frame, "A: {:6.2f}".format(cone.angle), (cone.x + 10, cone.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
        cv.putText(frame, "O: {:6.2f}".format(cone.offset), (cone.x + 10, cone.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)

        if len(cones) >= 2:
            cone = cones[1]
            cv.rectangle(frame, (cone.x, cone.y), ((cone.x + cone.w), (cone.y + cone.h)), (0, 255, 0), 2)
            cv.putText(frame, "D: {:6.2f}".format(cone.distance), (cone.x + 10, cone.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "A: {:6.2f}".format(cone.angle), (cone.x + 10, cone.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
            cv.putText(frame, "O: {:6.2f}".format(cone.offset), (cone.x + 10, cone.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)

            if len(cones) >= 3:
                cone = cones[2]
                cv.rectangle(frame, (cone.x, cone.y), ((cone.x + cone.w), (cone.y + cone.h)), (0, 255, 0), 2)
                cv.putText(frame, "D: {:6.2f}".format(cone.distance), (cone.x + 10, cone.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
                cv.putText(frame, "A: {:6.2f}".format(cone.angle), (cone.x + 10, cone.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
                cv.putText(frame, "O: {:6.2f}".format(cone.offset), (cone.x + 10, cone.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 2)
    
    fieldFrame = frame

    if networkTablesConnected:
        visionTable.putNumber("CubesFound", len(cubes))
        if len(cubes) >= 1:
            visionTable.putNumber("Cubes.0.distance", unwrap_or(cubes[0].distance, -9999.))
            visionTable.putNumber("Cubes.0.angle", unwrap_or(cubes[0].angle, -9999.))
            visionTable.putNumber("Cubes.0.offset", unwrap_or(cubes[0].offset, -9999.))
            if len(cubes) >= 2:
                visionTable.putNumber("Cubes.1.distance", unwrap_or(cubes[1].distance, -9999.))
                visionTable.putNumber("Cubes.1.angle", unwrap_or(cubes[1].angle, -9999.))
                visionTable.putNumber("Cubes.1.offset", unwrap_or(cubes[1].offset, -9999.))
                if len(cubes) >= 3:
                    visionTable.putNumber("Cubes.2.distance", unwrap_or(cubes[2].distance, -9999.))
                    visionTable.putNumber("Cubes.2.angle", unwrap_or(cubes[2].angle, -9999.))
                    visionTable.putNumber("Cubes.2.offset", unwrap_or(cubes[2].offset, -9999.))
        
        visionTable.putNumber("ConesFound", len(cones))
        if len(cones) >= 1:
            visionTable.putNumber("Cones.0.distance", unwrap_or(cones[0].distance, -9999.))
            visionTable.putNumber("Cones.0.angle", unwrap_or(cones[0].angle, -9999.))
            visionTable.putNumber("Cones.0.offset", unwrap_or(cones[0].offset, -9999.))
            if len(cones) >= 2:
                visionTable.putNumber("Cones.1.distance", unwrap_or(cones[1].distance, -9999.))
                visionTable.putNumber("Cones.1.angle", unwrap_or(cones[1].angle, -9999.))
                visionTable.putNumber("Cones.1.offset", unwrap_or(cones[1].offset, -9999.))
                if len(cones) >= 3:
                    visionTable.putNumber("Cones.2.distance", unwrap_or(cones[2].distance, -9999.))
                    visionTable.putNumber("Cones.2.angle", unwrap_or(cones[2].angle, -9999.))
                    visionTable.putNumber("Cones.2.offset", unwrap_or(cones[2].offset, -9999.))
    
    done += 1

def handle_tapes(frame, tapes):
    global done, tapeFrame
    if len(tapes) >= 1:

        tape = tapes[0]
        cv.rectangle(frame, (tape.x, tape.y), ((tape.x + tape.w), (tape.y + tape.h)), (0, 0, 255), 2)
        cv.putText(frame, "D: {:6.2f}".format(tape.distance), (tape.x + tape.w + 10, tape.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv.putText(frame, "A: {:6.2f}".format(tape.angle), (tape.x + tape.w + 10, tape.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        cv.putText(frame, "O: {:6.2f}".format(tape.offset), (tape.x + tape.w + 10, tape.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        if len(tapes) >= 2:
            tape = tapes[1]
            cv.rectangle(frame, (tape.x, tape.y), ((tape.x + tape.w), (tape.y + tape.h)), (0, 255, 0), 2)
            cv.putText(frame, "D: {:6.2f}".format(tape.distance), (tape.x + tape.w + 10, tape.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv.putText(frame, "A: {:6.2f}".format(tape.angle), (tape.x + tape.w + 10, tape.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv.putText(frame, "O: {:6.2f}".format(tape.offset), (tape.x + tape.w + 10, tape.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

            if len(tapes) >= 3:
                tape = tapes[2]
                cv.rectangle(frame, (tape.x, tape.y), ((tape.x + tape.w), (tape.y + tape.h)), (0, 255, 0), 2)
                cv.putText(frame, "D: {:6.2f}".format(tape.distance), (tape.x + tape.w + 10, tape.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv.putText(frame, "A: {:6.2f}".format(tape.angle), (tape.x + tape.w + 10, tape.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                cv.putText(frame, "O: {:6.2f}".format(tape.offset), (tape.x + tape.w + 10, tape.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                if len(tapes) >= 4:
                    tape = tapes[3]
                    cv.rectangle(frame, (tape.x, tape.y), ((tape.x + tape.w), (tape.y + tape.h)), (0, 255, 0), 2)
                    cv.putText(frame, "D: {:6.2f}".format(tape.distance), (tape.x + tape.w + 10, tape.y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv.putText(frame, "A: {:6.2f}".format(tape.angle), (tape.x + tape.w + 10, tape.y + 30), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                    cv.putText(frame, "O: {:6.2f}".format(tape.offset), (tape.x + tape.w + 10, tape.y + 45), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    
    tapeFrame = frame
    
    if networkTablesConnected:
        visionTable.putNumber("TapesFound", len(tapes))
        if len(tapes) >= 1:
            visionTable.putNumber("Tapes.0.distance", unwrap_or(tapes[0].distance, -9999.))
            visionTable.putNumber("Tapes.0.angle", unwrap_or(tapes[0].angle, -9999.))
            visionTable.putNumber("Tapes.0.offset", unwrap_or(tapes[0].offset, -9999.))
            visionTable.putNumber("Tapes.0.y", unwrap_or(tapes[0].y, -9999.))
            if len(tapes) >= 2:
                visionTable.putNumber("Tapes.1.distance", unwrap_or(tapes[1].distance, -9999.))
                visionTable.putNumber("Tapes.1.angle", unwrap_or(tapes[1].angle, -9999.))
                visionTable.putNumber("Tapes.1.offset", unwrap_or(tapes[1].offset, -9999.))
                visionTable.putNumber("Tapes.1.y", unwrap_or(tapes[1].y, -9999.))
                if len(tapes) >= 3:
                    visionTable.putNumber("Tapes.2.distance", unwrap_or(tapes[2].distance, -9999.))
                    visionTable.putNumber("Tapes.2.angle", unwrap_or(tapes[2].angle, -9999.))
                    visionTable.putNumber("Tapes.2.offset", unwrap_or(tapes[2].offset, -9999.))
                    visionTable.putNumber("Tapes.2.y", unwrap_or(tapes[2].y, -9999.))
                    if len(tapes) >= 4:
                        visionTable.putNumber("Tapes.3.distance", unwrap_or(tapes[3].distance, -9999.))
                        visionTable.putNumber("Tapes.3.angle", unwrap_or(tapes[3].angle, -9999.))
                        visionTable.putNumber("Tapes.3.offset", unwrap_or(tapes[3].offset, -9999.))
                        visionTable.putNumber("Tapes.3.y", unwrap_or(tapes[3].y, -9999.))

    done += 1

#Define main processing function
def main():

    global timeString, networkTablesConnected, visionTable, done

    time.sleep(startupSleep)


    #Define objects
    visionTable = None
    FRCWebCam.read_config_file(cameraFile)
    fieldCam = FRCWebCam('FIELD', timeString, videofile="FIELD_" + timeString, csname="field")
    tapeCam = FRCWebCam('TAPE', timeString, videofile="TAPE_" + timeString, csname="tapes")
    VisionBase.read_vision_file(visionFile)

    cubeLib = CubeVisionLibrary()
    coneLib = ConeVisionLibrary()
    tapeLib = TapeRectVisionLibrary()
    
    
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

            fieldCam.use_libs_async(cubeLib, coneLib, callback=handle_field_objects, name="field")
            tapeCam.use_libs_async(tapeLib, callback=handle_tapes, name="tapes")
            
            while done < 2:
                time.sleep(0.005)
            
            if videoTesting:
                
                cv.imshow("Field", fieldFrame)
                cv.imshow("Tapes", tapeFrame)

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