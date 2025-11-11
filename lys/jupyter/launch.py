import os
import subprocess
import signal
import atexit
import sys
import time
import ctypes


def launch_jupyter_lab():
    env = os.environ.copy()
    connection_file = os.getcwd() + "/.lys/lys_jupyter/connection/kernel_lys.json"
    env["EXISTING_CONNECTION_FILE"] = connection_file

    libc = ctypes.CDLL("libc.so.6")

    def _set_death_signal():
        libc.prctl(1, signal.SIGHUP)

    proc = subprocess.Popen(
        [
            "jupyter", "lab",
            "--no-browser",
            "--KernelProvisionerFactory.default_provisioner_name=existing-provisioner"
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=lambda: (os.setsid(), _set_death_signal())
    )

    cleaned = False

    def cleanup():
        nonlocal cleaned
        if cleaned:
            return
        cleaned = True

        print("Terminating JupyterLab ...")

        try:
            pgid = os.getpgid(proc.pid)
        except ProcessLookupError:
            return

        # ---- gentle shutdown ----
        try:
            os.killpg(pgid, signal.SIGTERM)
        except ProcessLookupError:
            return

        # ---- wait up to 5s ----
        for _ in range(10):
            if proc.poll() is not None:
                break
            time.sleep(0.5)

        # ---- force kill if needed ----
        if proc.poll() is None:
            print("Jupyter did not exit gracefully. Sending SIGKILL ...")
            try:
                os.killpg(pgid, signal.SIGKILL)
            except ProcessLookupError:
                pass

        try:
            proc.wait(timeout=3)
        except Exception:
            pass

    atexit.register(cleanup)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    signal.signal(signal.SIGHUP, lambda *args: cleanup())

    def _excepthook(t, v, tb):
        cleanup()
        sys.__excepthook__(t, v, tb)

    sys.excepthook = _excepthook
