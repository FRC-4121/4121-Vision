from platform import node as hostname
import importlib as imp

if __name__ == "__main__":
    imp.import_module(hostname()).main()
