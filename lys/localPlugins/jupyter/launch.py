import os
import subprocess
import signal
import atexit

def launch_jupyter_lab():
    env = os.environ.copy()
    env["EXISTING_CONNECTION_FILE"] = os.getcwd() + "/.lys/lys_jupyter/connection/kernel_lys.json"

    proc = subprocess.Popen(
        [
            "jupyter", "lab",
            "--no-browser",
            "--KernelProvisionerFactory.default_provisioner_name=existing-provisioner"
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid   # ← 新しいプロセスグループを作る
    )

    def cleanup():
        try:
            print("Terminating JupyterLab ...")
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except ProcessLookupError:
            pass

    atexit.register(cleanup)
