import numpy as np
from matplotlib import cm, markers
from matplotlib.lines import Line2D

from lys.Qt import QtCore, QtWidgets
from lys.widgets import ColormapSelection, ColorSelection, ScientificSpinBox
from lys.decorators import avoidCircularReference


from .ImageSettingsGUI import ImageColorAdjustBox
from .FontGUI import FontSelector


class _LineStyleAdjustBox(QtWidgets.QWidget):
    __stylelist = ['solid', 'dashed', 'dashdot', 'dotted', 'None']
    __widthlist = ["Linear", "Log", "Sqrt", "Square", "Expression"]
    styleChanged = QtCore.pyqtSignal(str)
    useSolidColorChanged = QtCore.pyqtSignal(bool)
    colorChanged = QtCore.pyqtSignal(str)
    useDataBasedWidthChanged = QtCore.pyqtSignal(bool)
    widthChanged = QtCore.pyqtSignal(float)
    widthRangeChanged = QtCore.pyqtSignal(float)
    widthExpressionChanged = QtCore.pyqtSignal(str)

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.__initlayout()

    def __initlayout(self):
        self.__useSolidColor = QtWidgets.QCheckBox("Solid Color")
        self.__useSolidColor.stateChanged.connect(self.__onUseSolidColorChanged)
        self.__color = ColorSelection()
        self.__color.colorChanged.connect(lambda c: self.colorChanged.emit(c))

        self.__style = QtWidgets.QComboBox()
        self.__style.addItems(self.__stylelist)
        self.__style.activated.connect(lambda: self.styleChanged.emit(self.__style.currentText()))

        self.__widthcheck = QtWidgets.QCheckBox("Data-based Width")
        self.__widthcheck.stateChanged.connect(self.__onWidthCheckChanged)
        
        self.__widthspin = QtWidgets.QDoubleSpinBox()
        self.__widthspin.valueChanged.connect(lambda: self.widthChanged.emit(self.__widthspin.value()))

        self.__widthcombo = QtWidgets.QComboBox()
        self.__widthcombo.addItems(self.__widthlist)
        self.__widthcombo.activated.connect(lambda: self.__onWidthComboChanged(self.__widthcombo.currentText()))

        self.__widthmax = QtWidgets.QDoubleSpinBox()
        self.__widthmax.setRange(0, np.inf)
        self.__widthmax.valueChanged.connect(lambda: self.widthRangeChanged.emit(self.__widthmax.value()))

        self.__widthexp = QtWidgets.QLineEdit()
        self.__expapply = QtWidgets.QPushButton("Apply")
        self.__expapply.clicked.connect(lambda: self.sizeExpressionChanged.emit(self.__sizeexp.text()))


        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel('Type'), 0, 0, 1, 2)
        layout.addWidget(self.__style, 0, 2, 1, 2)
        layout.addWidget(self.__useSolidColor, 1, 0, 1, 2)
        layout.addWidget(self.__color, 1, 2, 1, 2)
        layout.addWidget(self.__widthcheck, 2, 0, 1, 2)
        layout.addWidget(QtWidgets.QLabel('Width'), 2, 2, 1, 1)
        layout.addWidget(self.__widthspin, 2, 3, 1, 1)
        layout.addWidget(self.__widthcombo, 3, 0, 1, 2)
        layout.addWidget(QtWidgets.QLabel("max"), 3, 2, 1, 1)
        layout.addWidget(self.__widthmax, 3, 3, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Use 'z' for data values"), 4, 0, 1, 4)
        layout.addWidget(self.__widthexp, 5, 0, 1, 3)
        layout.addWidget(self.__expapply, 5, 3, 1, 1)
        layout.setRowStretch(6, 1)
        self.setLayout(layout)


    def setUseSolidColor(self, color):
        self.__useSolidColor.setChecked(color)

    def setWidth(self, width):
        self.__widthspin.setValue(width)

    def setStyle(self, style):
        self.__style.setCurrentText(style)
    
    def setColor(self, color):
        self.__color.setColor(color)
    
    def setDataBasedWidth(self, bool):
        self.__widthcheck.setChecked(bool)

    def setWidthRange(self, max):
        self.__widthmax.setValue(max)

    def setWidthExpression(self, expr):
        if expr in self.__widthlist[:-1]:
            self.__widthcombo.setCurrentText(expr)
        else:
            self.__widthcombo.setCurrentText(self.__widthlist[-1])
            self.__widthexp.setText(expr)

    def setEnabled(self, b):
        # print("setEnabled", b)
        self.__style.setEnabled(b)
        self.__useSolidColor.setEnabled(b)
        self.__widthcheck.setEnabled(b)
        self.__widthcombo.setEnabled(b)
        if b:
            self.__onUseSolidColorChanged()
            self.__onWidthCheckChanged()
        else:
            self.__color.setEnabled(False)
            self.__widthspin.setEnabled(False)
            self.__widthcombo.setEnabled(False)
            self.__widthmax.setEnabled(False)
            self.__widthexp.setEnabled(False)
            self.__expapply.setEnabled(False)
    
    def __onUseSolidColorChanged(self, state=None):
        if state is None:
            state = self.__useSolidColor.isChecked()
        self.__color.setEnabled(state)
        self.useSolidColorChanged.emit(state)

    def __onWidthCheckChanged(self, state=None):
        if state is None:
            state = self.__widthcheck.isChecked()
        self.__widthspin.setEnabled(not state)
        self.__widthcombo.setEnabled(state)
        self.__widthmax.setEnabled(state)
        if state:
            self.__onWidthComboChanged()
        else:
            self.__widthexp.setEnabled(False)
            self.__expapply.setEnabled(False)
        self.useDataBasedWidthChanged.emit(state)

    def __onWidthComboChanged(self, text=None):
        if text is None:
            text = self.__widthcombo.currentText()
        self.__widthexp.setEnabled(text == "Expression")
        self.__expapply.setEnabled(text == "Expression")
        if text != "Expression":
            self.widthExpressionChanged.emit(text)


class _MarkerStyleAdjustBox(QtWidgets.QWidget):
    __sizelist = ["Linear", "Log", "Sqrt", "Square", "Expression"]
    styleChanged = QtCore.pyqtSignal(str)
    fillingChanged = QtCore.pyqtSignal(str)
    sizeChanged = QtCore.pyqtSignal(float)
    thickChanged = QtCore.pyqtSignal(float)
    useSolidColorChanged = QtCore.pyqtSignal(bool)
    colorChanged = QtCore.pyqtSignal(str)
    useDataBasedSizeChanged = QtCore.pyqtSignal(bool)
    sizeRangeChanged = QtCore.pyqtSignal(float)
    sizeExpressionChanged = QtCore.pyqtSignal(str)

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        # self.__stylelist = list(Line2D.markers.values())
        self.__stylelist = ["None"] + [v for v in markers.MarkerStyle.markers.values()]
        self.__fillist = markers.MarkerStyle.fillstyles
        self.__initlayout()

    def __initlayout(self):
        self.__useSolidColor = QtWidgets.QCheckBox("Solid Color")
        self.__useSolidColor.stateChanged.connect(self.__onUseSolidColorChanged)
        self.__color = ColorSelection()
        self.__color.colorChanged.connect(lambda color: self.colorChanged.emit(color))

        self.__style = QtWidgets.QComboBox()
        self.__style.addItems(self.__stylelist)
        self.__style.activated.connect(lambda: self.styleChanged.emit(self.__style.currentText()))

        self.__fill = QtWidgets.QComboBox()
        self.__fill.addItems(self.__fillist)
        self.__fill.activated.connect(lambda: self.fillingChanged.emit(self.__fill.currentText()))

        self.__thickspin = QtWidgets.QDoubleSpinBox()
        self.__thickspin.valueChanged.connect(self.thickChanged.emit)

        self.__sizecheck = QtWidgets.QCheckBox("Data-based Size")
        self.__sizecheck.stateChanged.connect(self.__onSizeCheckChanged)
        
        self.__sizespin = QtWidgets.QDoubleSpinBox()
        self.__sizespin.valueChanged.connect(lambda: self.sizeChanged.emit(self.__sizespin.value()))

        self.__sizecombo = QtWidgets.QComboBox()
        self.__sizecombo.addItems(self.__sizelist)
        self.__sizecombo.activated.connect(lambda: self.__onSizeComboChanged(self.__sizecombo.currentText()))

        self.__sizemax = QtWidgets.QDoubleSpinBox()
        self.__sizemax.setRange(0, np.inf)
        self.__sizemax.valueChanged.connect(lambda: self.sizeRangeChanged.emit(self.__sizemax.value()))

        self.__sizeexp = QtWidgets.QLineEdit()
        self.__expapply = QtWidgets.QPushButton("Apply")
        self.__expapply.clicked.connect(lambda: self.sizeExpressionChanged.emit(self.__sizeexp.text()))

        layout = QtWidgets.QGridLayout()
        layout.addWidget(QtWidgets.QLabel('Type'), 0, 0, 1, 2)
        layout.addWidget(self.__style, 0, 2, 1, 2)
        layout.addWidget(self.__useSolidColor, 1, 0, 1, 2)
        layout.addWidget(self.__color, 1, 2, 1, 2)
        layout.addWidget(QtWidgets.QLabel('Filling'), 2, 0, 1, 1)
        layout.addWidget(self.__fill, 2, 1, 1, 1)
        layout.addWidget(QtWidgets.QLabel('Thick'), 2, 2, 1, 1)
        layout.addWidget(self.__thickspin, 2, 3, 1, 1)
        layout.addWidget(self.__sizecheck, 3, 0, 1, 2)
        layout.addWidget(QtWidgets.QLabel('Size'), 3, 2, 1, 1)
        layout.addWidget(self.__sizespin, 3, 3, 1, 1)
        layout.addWidget(self.__sizecombo, 4, 0, 1, 2)
        layout.addWidget(QtWidgets.QLabel("max"), 4, 2, 1, 1)
        layout.addWidget(self.__sizemax, 4, 3, 1, 1)
        layout.addWidget(QtWidgets.QLabel("Use 'z' for data values"), 5, 0, 1, 4)
        layout.addWidget(self.__sizeexp, 6, 0, 1, 3)
        layout.addWidget(self.__expapply, 6, 3, 1, 1)
        layout.setRowStretch(7, 1)
        self.setLayout(layout)

    def setStyle(self, marker):
        self.__style.setCurrentText(marker)

    def setFilling(self, filling):
        self.__fill.setCurrentText(filling)

    def setSize(self, size):
        self.__sizespin.setValue(size)

    def setThick(self, thick):
        self.__thickspin.setValue(thick)
    
    def setSizeRange(self, max):
        self.__sizemax.setValue(max)
    
    def setSizeExpression(self, expr):
        if expr in self.__sizelist[:-1]:
            self.__sizecombo.setCurrentText(expr)
        else:
            self.__sizecombo.setCurrentText(self.__sizelist[-1])
            self.__sizeexp.setText(expr)
    
    def setUseSolidColor(self, enabled):
        self.__useSolidColor.setChecked(enabled)
    
    def setColor(self, color):
        self.__color.setColor(color)
    
    def setDataBasedSize(self, enabled):
        self.__sizecheck.setChecked(enabled)
  
    def setEnabled(self, b):
        self.__style.setEnabled(b)
        self.__useSolidColor.setEnabled(b)
        self.__sizecheck.setEnabled(b)
        self.__sizecombo.setEnabled(b)
        self.__fill.setEnabled(b)
        self.__thickspin.setEnabled(b)
        if b:
            self.__onUseSolidColorChanged()
            self.__onSizeCheckChanged()
        else:
            self.__color.setEnabled(False)
            self.__sizespin.setEnabled(False)
            self.__sizecombo.setEnabled(False)
            self.__sizemax.setEnabled(False)
            self.__sizeexp.setEnabled(False)
            self.__expapply.setEnabled(False)

    def __onUseSolidColorChanged(self, state=None):
        if state is None:
            state = self.__useSolidColor.isChecked()
        self.__color.setEnabled(state)
        self.useSolidColorChanged.emit(state)

    def __onSizeCheckChanged(self, state=None):
        if state is None:
            state = self.__sizecheck.isChecked()
        self.__sizespin.setEnabled(not state)
        self.__sizecombo.setEnabled(state)
        self.__sizemax.setEnabled(state)
        if state:
            self.__onSizeComboChanged()
        else:
            self.__sizeexp.setEnabled(False)
            self.__expapply.setEnabled(False)
        self.useDataBasedSizeChanged.emit(state)

    def __onSizeComboChanged(self, text=None):
        if text is None:
            text = self.__sizecombo.currentText()
        self.__sizeexp.setEnabled(text == "Expression")
        self.__expapply.setEnabled(text == "Expression")
        if text != "Expression":
            self.sizeExpressionChanged.emit(text)


class AppearanceBox(QtWidgets.QWidget):
    def __init__(self, canvas):
        super().__init__()
        self._scatters = []

        self._colormap = ImageColorAdjustBox(canvas)

        self._line = _LineStyleAdjustBox(canvas)
        self._line.styleChanged.connect(lambda s: [scatter.setLineStyle(s) for scatter in self._scatters])
        self._line.useSolidColorChanged.connect(lambda b: [scatter.setLineColorByData(not b) for scatter in self._scatters])
        self._line.colorChanged.connect(lambda c: [scatter.setLineColor(c) for scatter in self._scatters])
        self._line.useDataBasedWidthChanged.connect(lambda b: [scatter.setLineWidthByData(b) for scatter in self._scatters])
        self._line.widthChanged.connect(lambda w: [scatter.setLineWidth(w) for scatter in self._scatters])
        self._line.widthRangeChanged.connect(lambda val: [scatter.setLineWidthRange(val) for scatter in self._scatters])
        self._line.widthExpressionChanged.connect(lambda expr: [scatter.setLineWidthExpression(expr) for scatter in self._scatters])

        self._marker = _MarkerStyleAdjustBox(canvas)
        self._marker.styleChanged.connect(lambda val: [scatter.setMarker(val) for scatter in self._scatters])
        self._marker.fillingChanged.connect(lambda val: [scatter.setMarkerFilling(val) for scatter in self._scatters])
        self._marker.thickChanged.connect(lambda val: [scatter.setMarkerThick(val) for scatter in self._scatters])
        self._marker.sizeChanged.connect(lambda val: [scatter.setMarkerSize(val) for scatter in self._scatters])
        self._marker.colorChanged.connect(lambda val: [scatter.setMarkerColor(val) for scatter in self._scatters])
        self._marker.sizeRangeChanged.connect(lambda val: [scatter.setMarkerSizeRange(val) for scatter in self._scatters])
        self._marker.sizeExpressionChanged.connect(lambda expr: [scatter.setMarkerSizeExpression(expr) for scatter in self._scatters])
        self._marker.useDataBasedSizeChanged.connect(lambda b: [scatter.setMarkerSizeByData(b) for scatter in self._scatters])
        self._marker.useSolidColorChanged.connect(lambda b: [scatter.setMarkerColorByData(not b) for scatter in self._scatters])

        layout = QtWidgets.QVBoxLayout()
        cmapgroup = QtWidgets.QGroupBox('Colormap')
        vlayout = QtWidgets.QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        vlayout.setSpacing(0)
        vlayout.addWidget(self._colormap)
        cmapgroup.setLayout(vlayout)
        layout.addWidget(cmapgroup)

        tab = QtWidgets.QTabWidget()
        tab.addTab(self._marker, "Marker")
        tab.addTab(self._line, "Line")
        layout.addWidget(tab)

        self.setLayout(layout)
        self.__setEnabled(False)

    def setScatters(self, scatters):
        self._update_scatter(scatters)
        # print("setScatters", len(scatters))
        # self._scatters = scatters
        if len(scatters) != 0:
            self._colormap.setData(scatters)

            self._line.setStyle(scatters[0].getLineStyle())
            self._line.setUseSolidColor(not scatters[0].getLineColorByData())
            self._line.setColor(scatters[0].getLineColor())
            self._line.setDataBasedWidth(scatters[0].getLineWidthByData())
            self._line.setWidth(scatters[0].getLineWidth())
            self._line.setWidthRange(scatters[0].getLineWidthRange())
            self._line.setWidthExpression(scatters[0].getLineWidthExpression())

            self._marker.setStyle(scatters[0].getMarker())
            self._marker.setSize(scatters[0].getMarkerSize())
            self._marker.setFilling(scatters[0].getMarkerFilling())
            self._marker.setThick(scatters[0].getMarkerThick())
            self._marker.setSizeRange(scatters[0].getMarkerSizeRange())
            self._marker.setSizeExpression(scatters[0].getMarkerSizeExpression())
            self._marker.setDataBasedSize(scatters[0].getMarkerSizeByData())
            self._marker.setUseSolidColor(not scatters[0].getMarkerColorByData())
            self._marker.setColor(scatters[0].getMarkerColor())
            self.__setEnabled(True)
        else:
            self.__setEnabled(False)

    def __setEnabled(self, b):
        # print("__setEnabled", b)
        self._colormap.setEnabled(b)
        self._line.setEnabled(b)
        self._marker.setEnabled(b)
    
    def _update_scatter(self, scatters):
        if len(self._scatters) > 0 and (len(scatters) == 0 or self._scatters[0] != scatters[0]):
            try:
                self._scatters[0].modified.disconnect(self._on_scatter_modified)
            except (TypeError, RuntimeError):
                pass

        if len(scatters) > 0:
            scatters[0].modified.connect(self._on_scatter_modified)

        self._scatters = scatters

    def _on_scatter_modified(self):
        self._colormap.setData(self._scatters)