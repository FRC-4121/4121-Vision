import threading
import sys
from typing import *

tls = threading.local()


# Get a TLS variable. Must have a given key and initializer function (that doesn't return None)
def get_tls(name: str, init):
    var = getattr(tls, name, None)
    if var is None:
        var = init()
        setattr(tls, name, var)
    return var


# Killable thread. Works like a normal Thread, but can be externally killed
class KillableThread(threading.Thread):
    def __init__(
        self,
        group=None,
        target: Callable = None,
        name: Optional[str] = None,
        args: Iterable = (),
        kwargs: Mapping[str, Any] = {},
        *,
        daemon: Optional[bool] = None
    ):
        threading.Thread.__init__(
            self, group, target, name, args, kwargs, daemon=daemon
        )
        self.killed = False

    def start(self):
        self.__run_backup = self.run
        self.run = self.__run
        threading.Thread.start(self)

    def __run(self):
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, event, arg):
        if event == "call":
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, event, arg):
        if self.killed:
            if event == "line":
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True
