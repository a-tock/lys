import os, json
from jupyter_client.kernelspec import KernelSpecManager

def generate_json():
    wd = os.getcwd()
    contents = {
        "argv": [
        "python",
        "-c",
        "import time; time.sleep(24*3600)"
        ],
        "display_name": "lys",
        "language": "python",
        "metadata": {
        "kernel_provisioner": {
            "provisioner_name": "existing-provisioner",
            "config": {
            "connection_file": wd + "/.lys/lys_jupyter/connection/kernel_lys.json",
            "startup_timeout": 30,
            "poll_interval": 0.2
            }
        }
        }
    }
    os.makedirs(wd + "/.lys/lys_jupyter/kernel_lys", exist_ok=True)
    os.makedirs(wd + "/.lys/lys_jupyter/connection", exist_ok=True)
    with open(wd + "/.lys/lys_jupyter/kernel_lys/kernel.json", "w") as f:
        json.dump(contents, f, indent=4)

def installKernel():
    kernel_dir = os.getcwd() + "/.lys/lys_jupyter/kernel_lys"
    ksm = KernelSpecManager()
    ksm.install_kernel_spec(str(kernel_dir), kernel_name="lys", user=True, replace=True)

def register():
    generate_json()
    installKernel()