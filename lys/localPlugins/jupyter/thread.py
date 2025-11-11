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

    tee_out = Tee(sys.stdout, out_orig)
    tee_err = Tee(sys.stderr, err_orig)
    sys.stdout = tee_out
    sys.stderr = tee_err

    try:
        app.start()
    finally:
        # --- kernel shutdown: prevent "event loop is closed" ---
        tee_out.close()
        tee_err.close()
        sys.stdout = out_orig
        sys.stderr = err_orig


def start_thread():
    t = threading.Thread(target=start_kernel, daemon=True)
    t.start()


class Tee:
    def __init__(self, primary, secondary):
        self.primary = primary
        self.secondary = secondary
        self._lock = threading.RLock()
        self.closed = False

    def write(self, data):
        if self.closed:
            return 0
        with self._lock:
            try:
                self.primary.write(data)
            except Exception:
                pass
            try:
                self.secondary.write(data)
            except Exception:
                pass
        return len(data)

    def flush(self):
        if self.closed:
            return
        with self._lock:
            try:
                self.primary.flush()
            except Exception:
                pass
            try:
                self.secondary.flush()
            except Exception:
                pass

    def close(self):
        """Mark Tee as closed so shutdown writes are ignored."""
        self.closed = True

    # 一部のコードが fileno/encoding を参照する場合があるので委譲しておく
    @property
    def encoding(self):
        return getattr(self.primary, "encoding", None)

    def fileno(self):
        return getattr(self.primary, "fileno", lambda: -1)()
