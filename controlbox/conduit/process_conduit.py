import subprocess

from controlbox.conduit.base import DefaultConduit
from controlbox.conduit.watchdog import ResourceWatchdog


class ProcessConduit(DefaultConduit):
    """ Provides a conduit to a locally hosted process. """

    def __init__(self, *args):
        """
        args: the process image name and any additional arguments required by the process.
        raises OSError and ValueError
        """
        super().__init__()
        self.process = None
        self._load(*args)

    def _load(self, *args):
        p = subprocess.Popen(
            " ".join(args), stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        self.process = p
        self.set_streams(p.stdout, p.stdin)

    @property
    def open(self):
        """
        The conduit is considered open if the underlying process is still set and alive.
        """
        return self.process is not None and \
            self.process.poll() is None

    def wait_for_exit(self):
        self.process.wait()

    def close(self):
        if self.process is not None:
            self.process.terminate()
            self.process.wait()
            self.process = None


class ProcessWatchdog(ResourceWatchdog):
    """ Monitors a folder for executables that can be instantiated. """

    def __init__(self, dir, pattern, connection_factory):
        super().__init__(connection_factory)
        self.dir = dir
        self.pattern = pattern

    def is_allowed(self, key, device):
        return self.pattern.match(key) and super().is_allowed(key, device)
