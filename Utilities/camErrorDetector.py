#!/usr/bin/env python

# System imports
import sys
import os

team4121home = os.environ.get("TEAM4121HOME")
if None == team4121home:
    team4121home = os.getcwd()

team4121config = os.environ.get("TEAM4121CONFIG")
if None == team4121config:
    team4121config = "2024"

# Setup paths
sys.path.append(team4121home + "/lib")
