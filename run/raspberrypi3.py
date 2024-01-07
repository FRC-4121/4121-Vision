import sys
import datetime
import time
import logging


#Setup paths
sys.path.extend(['/usr/local/lib/vmxpi', '../lib'])


#Team 4121 module imports
from navx import FRCNavx

#Set up basic logging
logging.basicConfig(level=logging.DEBUG)

navxTesting = 0
currentTime = time.localtime(time.time())
timeString = "{}-{}-{}_{}:{}:{}".format(currentTime.tm_year, currentTime.tm_mon, currentTime.tm_mday, currentTime.tm_hour, currentTime.tm_min, currentTime.tm_sec)

# Round all elements in a tuple, returning the formatted string
# tup is the tuple, p is the number of decimal places, and n is the number of digits in the number (to the left of the decimal)
def round_tuple(tup, p, n = 1):
    return '(' + ', '.join((("{:" + str(p + n + 2) + "." + str(p) + "f}").format(v) for v in tup)) + ')'

# Puts an iterable value to the network table
# Elements are added as name.0, name.1, name.2, ...
def put_iterable(table, name, tup):
    for (elem, count) in zip(tup, range(len(tup))):
        table.putNumber(name + "." + str(count), elem)

def main():

    global useNavx, timeString, networkTablesConnected
    
    navxLoopCount = 0
    
    navx = None
    visionTable = None
    navxTable = None
    
    navx = FRCNavx('NavxStream')
    timeString = navx.get_raw_time()
    useNavx = not navx.poisoned

    logFilename = 'logs/run/log_' + timeString + '.txt'
    with open(logFilename, 'w') as log_file:
        log_file.write('run started on {}.\n'.format(datetime.datetime.now()))
        log_file.write('')

        #Connect NetworkTables
        try:
            if networkTablesConnected:
                NetworkTables.initialize(server='10.41.21.2')
                visionTable = NetworkTables.getTable("vision")
                navxTable = NetworkTables.getTable("navx")
                networkTablesConnected = True
                log_file.write('Connected to Networktables on 10.41.21.2 \n')

                visionTable.putNumber("RobotStop", 0)
                if useNavx:
                    visionTable.putString("Time", timeString)
                else:
                    timeString = visionTable.getString("Time", timeString)
        except:
            log_file.write('Error:  Unable to connect to Network tables.\n')
            log_file.write('Error message: ', sys.exc_info()[0])
            log_file.write('\n')

        log_file.write("connected to table\n" if networkTablesConnected else "Failed to connect to table\n")
        stop = False
        #Start main processing loop
        while not stop:

            #####################
            # Process NavX Gyro #
            #####################

            #Get VMX gyro angle
            if useNavx:

                gyroInit = navxTable.getNumber("ZeroGyro", 0) if networkTablesConnected else 0  #Check for signal to re-zero gyro
                if gyroInit == 1:
                    navx.reset_gyro()
                    navxTable.putNumber("ZeroGyro", 0)      
                gyroAngle = navx.read_angle()  #Read gyro angle
                
                #Put gyro value in NetworkTables
                if networkTablesConnected:
                    navxTable.putNumber("GyroAngle", gyroAngle)
                    put_iterable(navxTable, "Orientation", navx.read_orientation())
                    put_iterable(navxTable, "Acceleration", navx.read_acceleration())
                    put_iterable(navxTable, "Velocity", navx.read_velocity())
                    put_iterable(navxTable, "Position", navx.read_position())

                
                navxLoopCount += 1
                if navxLoopCount + 1 == navxTesting:
                    print("angle: {:7.2f}\torientation: {}\tacceleration: {}\tvelocity: {}\tposition: {}".format(gyroAngle, round_tuple(navx.read_orientation(), 2, 3), round_tuple(navx.read_acceleration(), 4), round_tuple(navx.read_velocity(), 4), round_tuple(navx.read_position(), 4)))
                    navxLoopCount = 0
            else:
                gyroAngle = -9999  #Set default gyro angle
            
            
            #################################
            # Check for stopping conditions #
            #################################

            #Check for stop code from network tables
            if networkTablesConnected: 
                robotStop = visionTable.getNumber("RobotStop", 0)
                if robotStop == 1 or not networkTablesConnected:
                    break

        #Close the log file
        log_file.write('Run stopped on {}.'.format(datetime.datetime.now()))

if __name__ == "__main__":
    main()