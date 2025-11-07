from .thread import start_thread
from .register import register
from .launch import launch_jupyter_lab


def start_jupyter():
    register()
    start_thread()
    launch_jupyter_lab()
