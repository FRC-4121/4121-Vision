# -*- coding: utf-8 -*-
#!/usr/bin/env python3

####################################################################
#                                                                  #
#                       FRC Vision Library                         #
#                                                                  #
#  This class provides numerous methods and utilities for vision   #
#  processing during an FRC game.  The provided methods cover      #
#  finding standard game elements (balls, cubes, etc.) as well as  #
#  retroreflective vision targets in video frames.                 #
#                                                                  #
#  @Version: 1.0                                                   #
#  @Created: 2020-1-8                                              #
#  @Author: Team 4121                                              #
#                                                                  #
####################################################################

'''FRC Vision Library - Provides vision processing for game elements'''

# System imports
import os

# Module Imports
import cv2 as cv
import numpy as np 
import math

# Read vision settings file
def read_vision_file(file):

    # Define class fields
    visionFile = ""
    ball1_values = {}
    ball2_values = {}
    goal_values = {}
    tape_values = {}
    marker_values = {}

    # Declare local variables
    value_section = ''
    new_section = False

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

            # Split the line into parts
            split_line = clean_line.split(',')

            # Determine section of the file we are in
            if split_line[0].upper() == 'BALL1:':
                value_section = 'BALL1'
                new_section = True
            elif split_line[0].upper() == 'BALL2:':
                value_section = 'BALL2'
                new_section = True
            elif split_line[0].upper() == 'GOALTARGET:':
                value_section = 'GOALTARGET'
                new_section = True
            elif split_line[0].upper() == 'VISIONTAPE:':
                value_section = 'VISIONTAPE'
                new_section = True
            elif split_line[0].upper() == 'MARKER:':
                value_section = 'MARKER'
                new_section = True
            elif split_line[0] == '':
                value_section = ''
                new_section = True
            else:
                new_section = False

            # Take action based on section
            if new_section == False:
                if value_section == 'BALL1':
                    ball1_values[split_line[0].upper()] = split_line[1]
                elif value_section == 'BALL2':
                    ball2_values[split_line[0].upper()] = split_line[1]
                elif value_section == 'GOALTARGET':
                    goal_values[split_line[0].upper()] = split_line[1]
                elif value_section == 'VISIONTAPE':
                    tape_values[split_line[0].upper()] = split_line[1]
                elif value_section == 'MARKER':
                    marker_values[split_line[0].upper()] = split_line[1]
                else:
                    new_section = True
        
    except FileNotFoundError:
        return False
        
    return True

# Declare main routine
def main():

    read_vision_file('/home/pi/Team4121/Config/2022VisionSettings.txt')


#define main function
if __name__ == '__main__':
    main()