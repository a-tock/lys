import threading
import sys
import os

from ipykernel.kernelapp import IPKernelApp
from .kernel import lysKernel


def start_kernel():
    connection = os.getcwd() + "/.lys/lys_jupyter/connection/kernel_lys.json"

    out_orig, err_orig = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

    app = IPKernelApp.instance()
    app.kernel_class = lysKernel
    app.init_signal = lambda: None

    argv = [
        f"--IPKernelApp.connection_file={connection}",
        "--IPKernelApp.transport=tcp",
    ]
    app.initialize(argv)

    sys.stdout = Tee(sys.stdout, out_orig)
    sys.stderr = Tee(sys.stderr, err_orig)

    while True:
        app.start()


def start_thread():
    t = threading.Thread(target=start_kernel, daemon=True)
    t.start()


class Tee:
    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary
        self._lock = threading.RLock()

    def write(self, data):
        with self._lock:
            self.primary.write(data)
            self.secondary.write(data)

    def flush(self):
        with self._lock:
            try:
                self.primary.flush()
            except Exception:
                pass
            try:
                self.secondary.flush()
            except Exception:
                pass

    # 一部のコードが fileno/encoding を参照する場合があるので委譲しておく
    @property
    def encoding(self):
        return getattr(self.primary, "encoding", None)

    def fileno(self):
        return getattr(self.primary, "fileno", lambda: -1)()
