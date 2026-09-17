
import warnings
import copy
import numpy as np
import matplotlib as mpl
from matplotlib import lines, colors, markers
from matplotlib import cm
from matplotlib.collections import LineCollection
from lys.errors import NotImplementedWarning

from ..interface import CanvasData, LineData, ImageData, RGBData, VectorData, ContourData, ScatterData


def _setZ(obj, z):
    obj.set_zorder(z - 100000)


class _MatplotlibLine(LineData):
    """Implementation of LineData for matplotlib"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._obj = canvas.getAxes(axis).errorbar(wave.x, wave.data)

    def remove(self):
        self._obj.remove()

    def _updateData(self):
        self.__update()

    def _setVisible(self, visible):
        self._appearance['Visible'] = visible
        self._obj.lines[0].set_visible(visible)
        for line in self._obj.lines[1] + self._obj.lines[2]:
            if line:
                line.set_visible(visible)

        self.canvas().updateLegends()

    def _setZ(self, z):
        _setZ(self._obj.lines[0], z)
        for line in self._obj.lines[1] + self._obj.lines[2]:
            _setZ(line, z - 1)

    def _setColor(self, color):
        self._obj.lines[0].set_color(color)
        for line in self._obj.lines[1] + self._obj.lines[2]:
            line.set_color(color)
        self.canvas().updateLegends()

    def _setStyle(self, style):
        self._obj.lines[0].set_linestyle(style)
        self.canvas().updateLegends()

    def _setWidth(self, width):
        self._obj.lines[0].set_linewidth(width)
        for line in self._obj.lines[1]:
            line.set_markeredgewidth(width)
        for line in self._obj.lines[2]:
            line.set_linewidth(width)
        self.canvas().updateLegends()

    def _setMarker(self, marker):
        dic = {value: key for key, value in lines.Line2D.markers.items()}
        self._obj.lines[0].set_marker(dic[marker])
        self.canvas().updateLegends()

    def _setMarkerSize(self, size):
        self._obj.lines[0].set_markersize(size)
        self.canvas().updateLegends()

    def _setMarkerThick(self, thick):
        self._obj.lines[0].set_markeredgewidth(thick)
        self.canvas().updateLegends()

    def _setMarkerFilling(self, filling):
        self._obj.lines[0].set_fillstyle(filling)
        self.canvas().updateLegends()

    def __update(self, error=None, direction=None, capsize=None):
        self._obj.remove()
        wave = self.getFilteredWave()
        xerr = yerr = error
        if direction == "x" or direction is None:
            yerr = self._getErrorbarData(self.getErrorbar("y"))
        if direction == "y" or direction is None:
            xerr = self._getErrorbarData(self.getErrorbar("x"))
        if capsize is None:
            capsize = self.getCapSize()
        self._obj = self.canvas().getAxes(self._axis).errorbar(wave.x, wave.data, xerr=xerr, yerr=yerr, capsize=capsize)
        visible = self.getVisible()
        if visible is not None:
            self._setVisible(visible)
        z = self.getZOrder()
        if z is not None:
            self._setZ(z)
        color = self.getColor()
        if color is not None:
            self._setColor(color)
        style = self.getStyle()
        if style is not None:
            self._setStyle(style)
        width = self.getWidth()
        if width is not None:
            self._setWidth(width)
        marker = self.getMarker()
        if marker is not None:
            self._setMarker(marker)
        msize = self.getMarkerSize()
        if msize is not None:
            self._setMarkerSize(msize)
        mthick = self.getMarkerThick()
        if mthick is not None:
            self._setMarkerThick(mthick)
        mfill = self.getMarkerFilling()
        if mfill is not None:
            self._setMarkerFilling(mfill)
        self.canvas().updateLegends()

    def _setErrorbar(self, error, direction):
        self.__update(error, direction, self.getCapSize())

    def _setCapSize(self, capsize):
        self.__update(capsize=capsize)

    def _setLegendVisible(self, visible):
        self.canvas().updateLegends()

    def _setLegendLabel(self, label):
        self.canvas().updateLegends()


def _calcExtent2D(wav):
    xstart = wav.x[0]
    xend = wav.x[len(wav.x) - 1]
    ystart = wav.y[0]
    yend = wav.y[len(wav.y) - 1]
    dx = (xend - xstart) / (wav.data.shape[1] - 1)
    dy = (yend - ystart) / (wav.data.shape[0] - 1)
    return (xstart - dx / 2, xend + dx / 2, yend + dy / 2, ystart - dy / 2)


class _MatplotlibImage(ImageData):
    """Implementation of LineData for matplotlib"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._axis = axis
        self._obj = canvas.getAxes(axis).imshow(wave.data.swapaxes(0, 1), aspect='auto', extent=_calcExtent2D(wave), picker=True)
        self._colorbar = None
        self._cpos = (0, 0)
        self._csize = (0.04, 1)
        self.canvas().canvasResized.connect(self.__resized)

    def remove(self):
        if self._colorbar is not None:
            self._colorbar.remove()
        self._obj.remove()

    def _updateData(self):
        data = self.getFilteredWave().data.swapaxes(0, 1)
        self._obj.set_data(np.ma.masked_invalid(data))
        self._obj.set_extent(_calcExtent2D(self.getFilteredWave()))

    def _setVisible(self, visible):
        self._obj.set_visible(visible)

    def _setZ(self, z):
        _setZ(self._obj, z)

    def _setColormap(self, cmap):
        colormap = copy.copy(cm.get_cmap(cmap))
        if hasattr(colormap, "set_gamma"):
            colormap.set_gamma(self.getGamma())
        self._obj.set_cmap(colormap)

    def _setGamma(self, gam):
        colormap = copy.copy(cm.get_cmap(self.getColormap()))
        if hasattr(colormap, "set_gamma"):
            colormap.set_gamma(gam)
        self._obj.set_cmap(colormap)

    def _setColorRange(self, min, max):
        if self.isLog():
            norm = colors.LogNorm(vmin=min, vmax=max)
        else:
            norm = colors.Normalize(vmin=min, vmax=max)
        self._obj.set_norm(norm)

    def _setLog(self, log):
        min, max = self.getColorRange()
        if log:
            norm = colors.LogNorm(vmin=min, vmax=max)
        else:
            norm = colors.Normalize(vmin=min, vmax=max)
        self._obj.set_norm(norm)

    def _setOpacity(self, value):
        self._obj.set_alpha(value)

    def __showColorbar(self, visible, direction='vertical'):
        fig = self.canvas().getFigure()
        if visible:
            if self.getColorbarDirection() != direction:
                self._colorbar.remove()
                self._colorbar = None
            if self._colorbar is None:
                self._colorbar = fig.colorbar(self._obj, ax=self.canvas().getAxes(self._axis), orientation=direction)
                self._colorbar.ax.set_aspect("auto")
        else:
            if self._colorbar is not None:
                self._colorbar.remove()
                self._colorbar = None

    def _setColorbarVisible(self, visible):
        self.__showColorbar(visible, self.getColorbarDirection())

    def _setColorbarDirection(self, direction):
        self.__showColorbar(self.getColorbarVisible(), direction)

    def _setColorbarPosition(self, pos):
        self._cpos = pos
        self.__resized()

    def _setColorbarSize(self, size):
        self._csize = size
        self.__resized()

    def __resized(self):
        if self._colorbar is not None:
            m = self.canvas().getMargin()
            if self.getColorbarDirection() == "vertical":
                self._colorbar.ax.set_position([m[1] + self._cpos[0], m[2] + self._cpos[1], self._csize[0], (m[3] - m[2]) * self._csize[1]])
            else:
                self._colorbar.ax.set_position([m[0] + self._cpos[1], m[3] + self._cpos[0], (m[1] - m[0]) * self._csize[1], self._csize[0]])

    def colorbar(self):
        return self._colorbar


class _MatplotlibVector(VectorData):
    """Implementation of VectorData for matplotlib"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._axis = axis
        xx, yy = np.meshgrid(wave.x, wave.y)
        if wave.dtype == complex:
            self._obj = canvas.getAxes(axis).quiver(xx, yy, np.real(wave.data.T), np.imag(wave.data.T), pivot="mid")
        else:
            self._obj = canvas.getAxes(axis).quiver(xx, yy, np.real(wave.data[:, :, 0].T), np.imag(wave.data[:, :, 1].T), pivot="mid")
        canvas.axisRangeChanged.connect(self._updateData)

    def remove(self):
        self._obj.remove()

    def _updateData(self):
        X, Y = np.meshgrid(self.getFilteredWave().x, self.getFilteredWave().y)
        if self.getFilteredWave().dtype == complex:
            data_x = np.array(np.real(self.getFilteredWave().data.T))
            data_y = np.array(np.imag(self.getFilteredWave().data.T))
        else:
            data_x = self.getFilteredWave().data[:, :, 0].T
            data_y = self.getFilteredWave().data[:, :, 1].T
        rx, ry = self.canvas().getAxisRange(self._axis)
        if rx[0] > rx[1]:
            data_x = -data_x
        if ry[0] > ry[1]:
            data_y = -data_y
        self._obj.set_UVC(data_x, data_y)
        self._obj.set_offsets(np.array([X.flatten(), Y.flatten()]).T)

    def _setVisible(self, visible):
        self._obj.set_visible(visible)

    def _setZ(self, z):
        _setZ(self._obj, z)

    def _setPivot(self, pivot):
        self._obj.pivot = pivot

    def _setScale(self, scale):
        self._obj.scale = scale

    def _setWidth(self, width):
        self._obj.width = width / 100

    def _setColor(self, color):
        self._obj.set_color(color)


class _MatplotlibRGB(RGBData):
    """Implementation of RGBData for matplotlib"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        w = self.getRGBWave()
        self._obj = canvas.getAxes(axis).imshow(w.data.swapaxes(0, 1), aspect='auto', extent=_calcExtent2D(w), picker=True)
        self._colormap = None
        self.canvas().canvasResized.connect(self.__setColormap)

    def remove(self):
        self._obj.remove()

    def _updateData(self):
        wave = self.getRGBWave()
        self._obj.set_data(wave.data.swapaxes(0, 1))
        self._obj.set_extent(_calcExtent2D(wave))
        if self._colormap is not None:
            self._colormapImage.set_data(self.getColormapData().swapaxes(0, 1)[::-1, :])

    def _setVisible(self, visible):
        self._obj.set_visible(visible)

    def _setZ(self, z):
        _setZ(self._obj, z)

    def _setColormapVisible(self, visible):
        self.__setColormap(visible=visible)

    def _setColormapPosition(self, pos):
        self.__setColormap(pos=pos)

    def _setColormapSize(self, size):
        self.__setColormap(size=size)

    def __setColormap(self, visible=None, pos=None, size=None):
        if visible is None or not isinstance(visible, bool):
            visible = self.getColormapVisible()
        if pos is None:
            pos = self.getColormapPosition()
        if size is None:
            size = self.getColormapSize()
        if visible:
            if self._colormap is None:
                import warnings
                import matplotlib.cbook
                warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
                self._colormap = self.canvas().getFigure().add_axes([0, 0, 1, 1])
                self._colormap.spines['left'].set_visible(False)
                self._colormap.spines['right'].set_visible(False)
                self._colormap.spines['top'].set_visible(False)
                self._colormap.spines['bottom'].set_visible(False)
                self._colormap.get_yaxis().set_tick_params(left=False, right=False, labelright=False, labelleft=False, which="both")
                self._colormap.get_xaxis().set_tick_params(top=False, bottom=False, labeltop=False, labelbottom=False, which="both")
                self._colormapImage = self._colormap.imshow(self.getColormapData().swapaxes(0, 1)[::-1, :])
            m = self.canvas().getMargin()
            self._colormap.set_position([m[1] + pos[0] * (m[1] - m[0]), m[2] + pos[1] * (m[3] - m[2]), size, size])
        else:
            if self._colormap is not None:
                self._colormap.remove()
                self._colormap = None


class _MatplotlibContour(ContourData):
    """Implementation of ContourData for matplotlib"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self._axis = axis
        self._obj = canvas.getAxes(axis).contour(wave.data.T[::-1, :], [0.5], extent=_calcExtent2D(wave))

    def remove(self):
        if hasattr(self._obj, "remove"):
            self._obj.remove()
        else:
            for o in self._obj.collections:
                o.remove()

    def _updateData(self):
        w = self.getFilteredWave()
        self.remove()
        self._obj = self.canvas().getAxes(self._axis).contour(w.data.T[::-1, :], [0.5], extent=_calcExtent2D(w))

    def __update(self, level=None):
        if level is None:
            level = self.getLevel()
        self.remove()
        w = self.getFilteredWave()
        self._obj = self.canvas().getAxes(self._axis).contour(w.data.T[::-1, :], [level], extent=_calcExtent2D(w))
        color = self.getColor()
        style = self.getStyle()
        width = self.getWidth()
        if color is not None:
            self._setColor(color)
        if style is not None:
            self._setStyle(style)
        if width is not None:
            self._setWidth(width)

    def _setLevel(self, level):
        self.__update(level=level)

    def _setColor(self, color):
        if hasattr(self._obj, "set"):
            self._obj.set(color=color)
        else:
            for o in self._obj.collections:
                o.set_color(color)

    def _setStyle(self, style):
        if hasattr(self._obj, "set"):
            self._obj.set(linestyle=style)
        else:
            for o in self._obj.collections:
                o.set_linestyle(style)

    def _setWidth(self, width):
        if hasattr(self._obj, "set"):
            self._obj.set(linewidth=width)
        else:
            for o in self._obj.collections:
                o.set_linewidth(width)

    def _setVisible(self, visible):
        if hasattr(self._obj, "set"):
            self._obj.set(visible=visible)
        else:
            for o in self._obj.collections:
                o.set_visible(visible)

    def _setZ(self, z):
        if hasattr(self._obj, "set"):
            self._obj.set(zorder=z)
        else:
            for o in self._obj.collections:
                _setZ(o, z)


class _MatplotlibScatter(ScatterData):
    """Implementation of ScatterData for matplotlib"""

    def __init__(self, canvas, wave, axis):
        super().__init__(canvas, wave, axis)
        self.__reverseMarkerMap = {v: k for k, v in markers.MarkerStyle.markers.items() if isinstance(v, str)}
        self.__reverseMarkerMap.update({"None": "", "none": ""})
        self._axis = axis
        self._colorbar = None
        self._cpos = (0, 0)
        self._csize = (0.04, 1)
        x, y = wave.x[:,0], wave.x[:, 1]
        self._marker = canvas.getAxes(axis).scatter(x, y, c=wave.data)
        self._marker.set_edgecolors('face')
        self._updateLineData(wave)
        self._line = canvas.getAxes(axis).add_collection(LineCollection(self._lineAxis, array=wave.data))
        self.setMarker("circle")
        self.setColormap("viridis")
        self.setLineStyle("None")
        self._errorbar = canvas.getAxes(axis).errorbar(x, y, fmt='none')
        self.canvas().canvasResized.connect(self.__resized)

    def _setVisible(self, visible):
        self._marker.set_visible(visible)
        self._line.set_visible(visible)
        for line in self._errorbar.lines[1] + self._errorbar.lines[2]:
            if line:
                line.set_visible(visible)

    def remove(self):
        if self._colorbar is not None:
            self._colorbar.remove()
        self._marker.remove()
        self._line.remove()
        self._errorbar.remove()

    def _updateLineData(self, wave):
        self._lineAxis = []
        for i in range(wave.data.shape[0]):
            if i == 0:
                self._lineAxis.append([(wave.x[0,0], wave.x[0,1]), ((wave.x[0,0] + wave.x[1,0])/2, ((wave.x[0,1] + wave.x[1,1])/2))])
            elif i == wave.data.shape[0] - 1:
                self._lineAxis.append([((wave.x[i-1,0] + wave.x[i,0])/2, (wave.x[i-1,1] + wave.x[i,1])/2), (wave.x[i,0], wave.x[i,1])])
            else:
                self._lineAxis.append([((wave.x[i-1,0] + wave.x[i,0])/2, (wave.x[i-1,1] + wave.x[i,1])/2), ((wave.x[i,0] + wave.x[i+1,0])/2, (wave.x[i,1] + wave.x[i+1,1])/2)])

    def _updateData(self):
        wave = self.getFilteredWave()
        self._marker.set_offsets(wave.x)
        self._updateLineData(wave)
        self._line.set_segments(self._lineAxis)
        self.__updateErrorbar()
        self.__setColormapGamma()

        if self.getMarkerSizeByData():
            self._setMarkerSizeExpression(self.getMarkerSizeExpression())
        if self.getLineWidthByData():
            self._setLineWidthExpression(self.getLineWidthExpression())

    def _setZ(self, z):
        _setZ(self._marker, z)
        _setZ(self._line, z - 1)
        for line in self._errorbar.lines[1] + self._errorbar.lines[2]:
            if line:
                _setZ(line, z - 2)

    def _setColormap(self, cmap):
        self.__setColormapGamma(cmap=cmap)
        
    def _setGamma(self, gam):
        self.__setColormapGamma(gam=gam)
    
    def __setColormapGamma(self, cmap=None, gam=None):
        if cmap is None:
            cmap = self.getColormap()
        if gam is None:
            gam = self.getGamma()
        wave = self.getFilteredWave()
        colormap = copy.copy(cm.get_cmap(cmap))
        if hasattr(colormap, "set_gamma"):
            colormap.set_gamma(gam)

        if self.getMarkerColorByData():
            self._marker.set_array(wave.data)
            self._marker.set_cmap(colormap)
            self.__setMarkerColorWithFilling()
        
        if self.getLineColorByData():
            self._line.set_color(None)
            self._line.set_array(wave.data)
            self._line.set_cmap(colormap)
        
        self.__setColorRangeAndLog()

    def _setColormapOpacity(self, value):
        if self.getMarkerColorByData():
            self._marker.set_alpha(value)
        if self.getLineColorByData():
            self._line.set_alpha(value)
        self.canvas().updateLegends()

    def _setColorRange(self, min, max):
        self.__setColorRangeAndLog(range=(min, max))

    def _setLog(self, log):
        self.__setColorRangeAndLog(log=log)
    
    def __setColorRangeAndLog(self, range=None, log=None):
        if range is None:
            range = self.getColorRange()
            if range is None:
                self.canvas().updateLegends()
                return
        if log is None:
            log = self.isLog()

        if log:
            norm = colors.LogNorm(vmin=range[0], vmax=range[1])
        else:
            norm = colors.Normalize(vmin=range[0], vmax=range[1])
        if self.getMarkerColorByData():
            self._marker.set_norm(norm)
        if self.getLineColorByData():
            self._line.set_norm(norm)

        self.canvas().updateLegends()

    def __showColorbar(self, visible, direction='vertical'):
        fig = self.canvas().getFigure()
        if visible:
            if self.getColorbarDirection() != direction:
                self._colorbar.remove()
                self._colorbar = None
            if self._colorbar is None:
                self._colorbar = fig.colorbar(self._marker, ax=self.canvas().getAxes(self._axis), orientation=direction)
                self._colorbar.ax.set_aspect("auto")
        else:
            if self._colorbar is not None:
                self._colorbar.remove()
                self._colorbar = None

    def _setColorbarVisible(self, visible):
        self.__showColorbar(visible, self.getColorbarDirection())

    def _setColorbarDirection(self, direction):
        self.__showColorbar(self.getColorbarVisible(), direction)

    def _setColorbarPosition(self, pos):
        self._cpos = pos
        self.__resized()

    def _setColorbarSize(self, size):
        self._csize = size
        self.__resized()

    def __resized(self):
        if self._colorbar is not None:
            m = self.canvas().getMargin()
            if self.getColorbarDirection() == "vertical":
                self._colorbar.ax.set_position([m[1] + self._cpos[0], m[2] + self._cpos[1], self._csize[0], (m[3] - m[2]) * self._csize[1]])
            else:
                self._colorbar.ax.set_position([m[0] + self._cpos[1], m[3] + self._cpos[0], (m[1] - m[0]) * self._csize[1], self._csize[0]])

    def colorbar(self):
        return self._colorbar

    def _setMarker(self, marker):
        marker = self.__reverseMarkerMap.get(marker, marker)
        new_marker = markers.MarkerStyle(marker=marker, fillstyle=self.getMarkerFilling())
        self._marker.set_paths([new_marker.get_path().transformed(new_marker.get_transform())])
        self.canvas().updateLegends()

    def _setMarkerColor(self, color):
        self._marker.set_array(None)
        self._marker.set_color(color)
        self.__setMarkerColorWithFilling()
        for line in self._errorbar.lines[1] + self._errorbar.lines[2]:
            if line:
                line.set_color(color)
        self.canvas().updateLegends()
    
    def _setMarkerSizeRange(self, max):
        self._setMarkerSize(self.__evaluateExpression(self.getMarkerSizeExpression(), max))

    def __evaluateExpression(self, expression, max):
        abs_data = np.abs(self.getFilteredWave().data)
        if expression == "Linear":
            return abs_data / np.max(abs_data) * max
        elif expression == "Log":
            abs_data = abs_data / np.max(abs_data) * 9
            return np.log10(abs_data + 1) * max
        elif expression == "Sqrt":
            abs_data = np.sqrt(abs_data)
            return abs_data / np.max(abs_data) * max
        elif expression == "Square":
            abs_data = abs_data ** 2
            return abs_data / np.max(abs_data) * max
        else:
            z = abs_data
            arr = eval(expression)
            return arr / np.max(arr) * max

    def _setMarkerSizeExpression(self, expression):
        self._setMarkerSize(self.__evaluateExpression(expression, self.getMarkerSizeRange()))

    def _setMarkerOpacity(self, opacity):
        self._marker.set_alpha(opacity)
        self.canvas().updateLegends()

    def _setMarkerSize(self, size):
        if not hasattr(size, "__iter__"):
            size = [size]
        size = np.array(size)**2
        self._marker.set_sizes(size)
        self.canvas().updateLegends()

    def _setMarkerThick(self, thick):
        if not hasattr(thick, "__iter__"):
            thick = [thick]
        self._marker.set_linewidth(thick)
        self.__setMarkerColorWithFilling()
        self.canvas().updateLegends()

    def _setMarkerFilling(self, filling):
        marker = self.getMarker()
        if marker in ["None", "none", "nothing"]:
            marker = ''
        marker = self.__reverseMarkerMap.get(marker, marker)
        new_marker = markers.MarkerStyle(marker=marker, fillstyle=filling)
        self._marker.set_paths([new_marker.get_path().transformed(new_marker.get_transform())])
        self.__setMarkerColorWithFilling(filling)
        self.canvas().updateLegends()
    
    def __setMarkerColorWithFilling(self, filling=None):
        if filling is None:
            filling = self.getMarkerFilling()

        if filling == "none":
            self._marker.set_edgecolor(None if self.getMarkerColorByData() else self.getMarkerColor())
            self._marker.set_facecolor('none')
        else:
            self._marker.set_facecolor(None if self.getMarkerColorByData() else self.getMarkerColor())
            self._marker.set_edgecolor('face')

    def _setLineStyle(self, style):
        if style == "None":
            self._line.set_linewidth(0)
        else:
            self.setLineWidthByData(self.getLineWidthByData())
            self._line.set_linestyle(style)
        self.canvas().updateLegends()

    def _setLineWidth(self, width):
        if self.getLineStyle() == "None":
            return
        self._line.set_linewidth(width)
        self.canvas().updateLegends()

    def _setLineColor(self, color):
        self._line.set_array(None)
        self._line.set_color(color)
        self.canvas().updateLegends()
    
    def _setLineWidthRange(self, max):
        self._setLineWidth(self.__evaluateExpression(self.getLineWidthExpression(), max))
        self.canvas().updateLegends()

    def _setLineWidthExpression(self, expression):
        self._setLineWidth(self.__evaluateExpression(expression, self.getLineWidthRange()))
        self.canvas().updateLegends()
      
    def _setLineOpacity(self, opacity):
        self._line.set_alpha(opacity)
        self.canvas().updateLegends()

    def __updateErrorbar(self, error=None, direction=None, capsize=None):
        self._errorbar.remove()
        wave = self.getFilteredWave()
        xerr = yerr = error
        if direction == "x" or direction is None:
            yerr = self._getErrorbarData(self.getErrorbar("y"))
        if direction == "y" or direction is None:
            xerr = self._getErrorbarData(self.getErrorbar("x"))
        if capsize is None:
            capsize = self.getCapSize()
        self._errorbar = self.canvas().getAxes(self._axis).errorbar(wave.x[:,0], wave.x[:,1], xerr=xerr, yerr=yerr, capsize=capsize, fmt='none')
        self._setVisible(self.getVisible())
        self._setZ(self.getZOrder())
        for line in self._errorbar.lines[1] + self._errorbar.lines[2]:
            if line:
                line.set_color(self.getMarkerColor())
        self.canvas().updateLegends()

    def _setErrorbar(self, error, direction):
        self.__updateErrorbar(error, direction)

    def _setCapSize(self, capsize):
        self.__updateErrorbar(capsize=capsize)

    def _setLegendVisible(self, visible):
        self._appearance["legendVisible"] = visible
        self.canvas().updateLegends()

    def _setLegendLabel(self, label):
        self._appearance["legendLabel"] = label
        self.canvas().updateLegends()


class _MatplotlibData(CanvasData):
    def _append1d(self, wave, axis):
        return _MatplotlibLine(self.canvas(), wave, axis)

    def _append2d(self, wave, axis):
        return _MatplotlibImage(self.canvas(), wave, axis)

    def _append3d(self, wave, axis):
        return _MatplotlibRGB(self.canvas(), wave, axis)

    def _appendContour(self, wav, axis):
        return _MatplotlibContour(self.canvas(), wav, axis)

    def _appendVectorField(self, wav, axis):
        return _MatplotlibVector(self.canvas(), wav, axis)
    
    def _appendScatter(self, wav, axis):
        return _MatplotlibScatter(self.canvas(), wav, axis)

    def _remove(self, data):
        data.remove()
