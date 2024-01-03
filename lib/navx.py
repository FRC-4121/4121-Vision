##################################################################
#                                                                #
#                       FRC Navx Library                         #
#                                                                #
#  This class is a wrapper around the HAL-Navx libraries.  This  #
#  class provides threading of the Navx board interactions.      #
#                                                                #
#  @Version: 1.0                                                 #
#  @Created: 2020-2-11                                           #
#  @Author: Team 4121                                            #
#                                                                #
##################################################################

'''FRC Navx Library - Provides threaded methods and utilities for Navx board'''


sys.path.append('/usr/local/lib/vmxpi/')

import sys
import importlib as imp
from typing import *
import time
import datetime
import vmxpi_hal_python as vmxpi


# Class for interfacing with the NavX boards
class FRCNavx:

    # Initialize self. Include whether or not we should sleep to initialize it
    def __init__(self, name: str, sleep: bool = True):

        self.vmx = vmxpi.VMXPi(False, 50)

        if self.vmx.IsOpen(): # board is powered, connected, and in a valid state
            # Reset Navx and initialize time
            self.reset(sleep)
            self.time = self.vmx.getTime().GetRTCTime()
            self.date = self.vmx.getTime().GetRTCDate()
            self.poisoned = False
        else:
            # Log error if VMX didn't open properly
            # Get current time as a string
            currentTime = time.localtime(time.time())
            timeString = str(currentTime.tm_year) + str(currentTime.tm_mon) + str(currentTime.tm_mday) + str(currentTime.tm_hour) + str(currentTime.tm_min)

            # Open a log file
            logFilename = '../logs/navx/log_' + timeString + '.txt'
            with open(logFilename, 'w') as log_file:
                log_file.write('Navx initialized on %s.\n' % datetime.datetime.now())
                log_file.write('')

                # Write error message
                log_file.write('Error:  Unable to open VMX Client.\n')
                log_file.write('\n')
                log_file.write('        - Is pigpio (or the system resources it requires) in use by another process?\n')
                log_file.write('        - Does this application have root privileges?')
            self.poisoned = True

        # Set name of Navx thread
        self.name = name

        # Initialize Navx values
        self.angle = 0.0
        self.yaw = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.pitchOffset = 0.0
        self.time = []
        self.date = []
       

    # Get the angle from straight ahead
    def read_angle(self) -> float:

        self.angle = round(self.vmx.getAHRS().GetAngle(), 2)
        return self.angle


    # Get the yaw
    def read_yaw(self) -> float:

        self.yaw = round(self.vmx.getAHRS().GetYaw(), 2)
        return self.yaw


    # Get the pitch
    def read_pitch(self) -> float:

        self.pitch = round(self.vmx.getAHRS().GetPitch() - self.pitchOffset, 2)
        return self.pitch

    # Get the roll
    def read_roll(self) -> float:

        self.roll = round(self.vmx.getAHRS().GetRoll(), 2)
        return self.roll


    # Reset the gyroscope, possibly sleeping to give it time to reinitialize.
    def reset(self, sleep: bool = True):

        if sleep:
            time.sleep(15)
        
        ahrs = self.vmx.getAHRS()
        ahrs.Reset()
        ahrs.ZeroYaw()
        self.pitchOffset = ahrs.GetPitch()

    # Get the tuple (yaw, pitch, roll)
    def read_orientation(self) -> Tuple[float, float, float]:
        return (self.read_yaw(), self.read_pitch(), self.read_roll())

    # Get acceleration vector as a tuple
    def read_acceleration(self) -> Tuple[float, float, float]:
        ahrs = self.vmx.getAHRS()
        return (ahrs.GetWorldLinearAccelX(), ahrs.GetWorldLinearAccelY(), ahrs.GetWorldLinearAccelZ())

    # Get velocity as a tuple
    def read_velocity(self) -> Tuple[float, float, float]:
        ahrs = self.vmx.getAHRS()
        return (ahrs.GetVelocityX(), ahrs.GetVelocityY(), ahrs.GetVelocityZ())
    
    # Get position (displacement) as a tuple
    def read_position(self) -> Tuple[float, float, float]:
        ahrs = self.vmx.getAHRS()
        return (ahrs.GetDisplacementX(), ahrs.GetDisplacementY(), ahrs.GetDisplacementZ())
    

    # Get the time from the RTC
    def read_time(self):

        self.time = self.vmx.getTime().GetRTCTime()
        return self.time
    

    # Get the date from the RTC
    def read_date(self):

        self.date = self.vmx.getTime().GetRTCDate()
        return self.date
    

    # Set the time, taking hours, minutes, and seconds
    def set_time(self, newtime: Tuple[int, int, int]) -> bool:

        success = self.vmx.getTime().SetRTCTime(newtime[0], 
                                                newtime[1],
                                                newtime[2])
        
        return success
    

    # Set the date, taking a tuple
    def set_date(self, newdate: Tuple[int, int, int, int]) -> bool:

        success = self.vmx.getTime().SetRTCDate(newdate[0],
                                                newdate[1],
                                                newdate[2],
                                                newdate[3])

        return success
    

    # Define get raw time method
    def get_raw_time(self) -> str:

        currentTime = self.read_time()
        currentDate = self.read_date()
        timeString = str(self.get_year(currentDate[4])) + str(currentDate[3]) + str(currentDate[2]) + str(currentTime[1]) + str(currentTime[2])
        return timeString
        

    # Get the name of a weekday from its number
    def get_day_name(self, weekday: int) -> str:
        return ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"][weekday % 7]
    

    # Define month conversion method
    def get_month_name(self, month: int):
        return [
            "December",
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November"
        ][month % 12]

