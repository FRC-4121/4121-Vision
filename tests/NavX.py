##############################################################
#                                                            #
#                  VMXPI NavX Test App                       #
#                                                            #
#  This file contains a program for testing the VMXPi board  #
#  from Kuai Labs.  This program uses methods out of the     #
#  NavX library for getting direction info from the board.   #
#  the web cam.                                              #
#                                                            #
#  @Version: 1.0                                             #
#  @Created: 2021-09-28                                      #
#  @Author: Team 4121                                        #
#                                                            #
##############################################################

"""VMXPi test application"""

# System imports
import sys
import os

# Module imports
import time
import logging

# Setup paths
sys.path.extend(['/usr/local/lib/vmxpi/', '../lib'])

# Team 4121 module imports
from navx import FRCNavx

# Set up basic logging
logging.basicConfig(level=logging.DEBUG)

# Define main method
def main():

    # Declare variables
    navx = ''

    # Initialize NavX object
    try:
        navx = FRCNavx('NavxStream')
    except:
        print('Unable to initialize NavX object')

    # Get current time as a string
    try:
        timeString = navx.get_raw_time()
        print(timeString)
    except:
        print('Unable to get time from NavX')



# Run main function
if __name__ == '__main__':
    main()



