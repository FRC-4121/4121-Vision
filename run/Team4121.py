from platform import node as hostname
import importlib as imp
import sys


if __name__ == "__main__":
    sys.path.append("lib")
    imp.import_module(hostname()).main()
