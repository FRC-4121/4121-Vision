#!/usr/bin/env python3

from platform import node as hostname
import importlib as imp
import sys


if __name__ == "__main__":
    imp.import_module(hostname()).main()
