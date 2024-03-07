from ctypes import CDLL

libc = CDLL("libc.so.6")


def flush():
    libc.fflush(None)
    libc.sync()
