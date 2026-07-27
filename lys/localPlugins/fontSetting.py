import os
import numpy as np
from lys import glb
from lys.Qt import QtWidgets, QtGui

_fontPath = ".lys/settings/font.npy"


def _applyFontCss(font: QtGui.QFont):
    styles = [
        f'font-family: "{font.family()}";',
        f'font-size: {font.pointSize()}pt;',
    ]
    if font.bold():
        styles.append("font-weight: bold;")
    if font.italic():
        styles.append("font-style: italic;")

    font_css = f"QWidget {{ {' '.join(styles)} }}"

    app = QtWidgets.QApplication.instance()
    if app:
        app.setStyleSheet(font_css)

    glb.mainWindow()._current_font = font


def _getCurrentFont() -> QtGui.QFont:
    return getattr(glb.mainWindow(), "_current_font", glb.mainWindow().font())


def _register():
    menu = glb.mainWindow().menuBar()
    font = menu.addMenu("Font")
    font.addAction("Set Font").triggered.connect(_setFont)
    default = font.addMenu("Default")
    default.addAction("Save as default").triggered.connect(_saveAsDefault)
    default.addAction("Load default").triggered.connect(_loadDefault)
    default.addAction("Initialize").triggered.connect(_initializeFont)


def _setFont():
    current_font = _getCurrentFont()
    font, ok = QtWidgets.QFontDialog.getFont(current_font, glb.mainWindow())
    if ok:
        _applyFontCss(font)


def _saveAsDefault():
    os.makedirs(".lys/settings/", exist_ok=True)
    dic = {}
    font = _getCurrentFont()
    dic["font"] = font.toString()
    np.save(_fontPath, dic)


def _loadDefault():
    os.makedirs(".lys/settings/", exist_ok=True)
    if os.path.exists(_fontPath):
        dic = np.load(_fontPath, allow_pickle=True).item()
        font = QtGui.QFont()
        font.fromString(dic["font"])
        _applyFontCss(font)


def _initializeFont():
    default_font = QtGui.QFont()
    _applyFontCss(default_font)


_register()
_loadDefault()