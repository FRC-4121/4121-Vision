# -----------------------------------------------------------------
#
# FRC Navx Library
#
# This class is a wrapper around the HAL-Navx libraries.  This
# class provides threading of the Navx board interactions.
#
# @Version: 1.0
#
# @Created: 2020-2-11
#
# @Author: Team 4121
#
# -----------------------------------------------------------------
"""Focal length detector - Determines focal length of cameras"""

#!/usr/bin/env python3

# System imports
import sys
import os

visionUser = os.environ.get("USER")
if None == visionUser:
    visionUser = "pi"

team4121home = os.environ.get("TEAM4121HOME")
if None == team4121home:
    team4121home = os.getcwd()

# Setup paths
sys.path.append("/home/" + visionUser + "/.local/lib/python3.9/site-packages")
sys.path.append("/home/" + visionUser + "/.local/lib/python3.7/site-packages")
sys.path.append(team4121home + "/Motion")
sys.path.append(team4121home + "/Vision")

# TODO: implement stuff
