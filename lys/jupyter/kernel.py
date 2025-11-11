import io
import sys
import builtins
import traceback
from contextlib import redirect_stdout, redirect_stderr

from ipykernel.kernelbase import Kernel
from .shell import run_in_gui_thread


class lysKernel(Kernel):
    implementation = "lysKernel"
    implementation_version = "1.0"
    language = "python"
    language_version = "{}.{}".format(sys.version_info.major, sys.version_info.minor)
    language_info = {"name": "python", "mimetype": "text/x-python", "file_extension": ".py"}
    banner = "lys Python Kernel"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # セッションごとの実行環境（REPL の環境）
        self.env = {}
        # input() を Jupyter の stdin チャネル経由にする
        self.env["__name__"] = "__main__"
        self.env["__package__"] = None
        self.env["__builtins__"] = builtins
        self.env["input"] = self._jupyter_input

        self._install_comm_noops()

    def _install_comm_noops(self):
        # shell チャネルの未知メッセージを潰す
        self.shell_handlers['comm_open'] = self._handle_comm_open
        # self.shell_handlers['comm_msg'] = self._handle_comm_msg

    def _handle_comm_open(self, stream, ident, parent):
        return

    def _jupyter_input(self, prompt=""):
        return self.raw_input(prompt)

    def do_execute(self, code, silent, store_history=True, user_expressions=None, allow_stdin=False):
        self.send_response(self.iopub_socket, "status", {"execution_state": "busy"})

        if not silent:
            self.send_response(self.iopub_socket, "execute_input", {"code": code, "execution_count": self.execution_count})

        stdout, stderr = io.StringIO(), io.StringIO()
        status = "ok"

        try:
            with redirect_stdout(stdout), redirect_stderr(stderr):
                result_obj = self._exec(code)

            out = stdout.getvalue()
            if out:
                self.send_response(self.iopub_socket, "stream", {"name": "stdout", "text": out})

            err = stderr.getvalue()
            if err:
                self.send_response(self.iopub_socket, "stream", {"name": "stderr", "text": err})

            if (not silent) and (result_obj is not None):
                data = {"text/plain": repr(result_obj)}
                self.send_response(self.iopub_socket, "execute_result", {"execution_count": self.execution_count, "data": data, "metadata": {}})

        except Exception:
            status = "error"
            etb = traceback.format_exc().splitlines()
            self.send_response(self.iopub_socket, "error", {"ename": "Error", "evalue": "Execution failed", "traceback": etb})

        # 実行終了
        self.send_response(self.iopub_socket, "status", {"execution_state": "idle"})

        # shell チャネルの reply（完了合図）
        return {"status": status, "execution_count": self.execution_count, "payload": [], "user_expressions": {}, }

    def _exec(self, code):
        from lys import glb
        s = glb.shell()
        mode, compiled = self._compile(code)
        if mode == "eval":
            return run_in_gui_thread(s.eval, code)
        else:
            return run_in_gui_thread(s.exec, code)

    def _compile(self, code: str):
        """
        1) 式なら eval 用、2) それ以外は exec 用 にコンパイル。
        """
        try:
            # “単一式”として評価できる?
            c = compile(code, "<cell>", "eval")
            return ("eval", c)
        except SyntaxError:
            # 文として実行
            c = compile(code, "<cell>", "exec")
            return ("exec", c)

    def do_shutdown(self, restart):
        from lys import glb
        s = glb.shell()

        # if hasattr(s, "request_interrupt"):
        #    s.request_interrupt()

        # if restart and hasattr(s, "reset"):
        #    s.reset()

        if restart:
            self.execution_count = 0

        return {"status": "ok", "restart": restart}

    def interrupt_kernel(self):
        from lys import glb
        s = glb.shell()
        # if hasattr(s, "request_interrupt"):
        #    s.request_interrupt()   # 自作: 実行中なら KeyboardInterrupt を発生させる等

        return {"status": "ok"}
