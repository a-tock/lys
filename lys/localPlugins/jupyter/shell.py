from lys.Qt import QtCore, QtWidgets

class MainThreadCaller(QtCore.QObject):
    _call_req = QtCore.pyqtSignal(object, tuple, dict)
    _call_done = QtCore.pyqtSignal(object, object)  # (result, exception)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._call_req.connect(self._on_call, QtCore.Qt.QueuedConnection)

    @QtCore.pyqtSlot(object, tuple, dict)
    def _on_call(self, fn, args, kwargs):
        try:
            res = fn(*args, **kwargs)
            self._call_done.emit(res, None)
        except BaseException as e:
            self._call_done.emit(None, e)


def run_in_gui_thread(fn, *args, **kwargs):
    app = QtWidgets.QApplication.instance()
    gui_thread = app.thread()
    if QtCore.QThread.currentThread() is gui_thread:
        return fn(*args, **kwargs)  # すでにGUIスレッド

    # GUIスレッドに常駐する呼び出し器を用意（1回作って保持推奨）
    caller = getattr(app, "_main_caller", None)
    if caller is None:
        caller = MainThreadCaller()
        caller.moveToThread(gui_thread)   # GUIスレッド所属にする
        app._main_caller = caller

    loop = QtCore.QEventLoop()
    result_holder = {"res": None, "exc": None}

    def on_done(res, exc):
        result_holder["res"] = res
        result_holder["exc"] = exc
        loop.quit()

    caller._call_done.connect(on_done)
    caller._call_req.emit(fn, args, kwargs)  # GUIスレッドへ投げる
    loop.exec_()  # 完了まで待機

    caller._call_done.disconnect(on_done)
    if result_holder["exc"] is not None:
        raise result_holder["exc"]
    return result_holder["res"]