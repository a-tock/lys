import numpy as np
from ..interface import CanvasLegend, FontInfo
from matplotlib import markers, lines, pyplot


class _MatplotlibLegend(CanvasLegend):
    """Implementation of CanvasLegend for matplotlib"""

    def __init__(self, canvas):
        super().__init__(canvas)
        self._family = None
        self._pos = None
        self._vis = True
        self.__reverseMarkerMap = {v: k for k, v in markers.MarkerStyle.markers.items() if isinstance(v, str)}
        self.__reverseMarkerMap.update({"None": "", "none": ""})
        self.canvas().dataChanged.connect(self.updateLegends)

    def updateLegends(self):
        lines = [line for line in self.canvas().getLines() if line.getLegendVisible() and line.getVisible()]
        objs = [line._obj for line in lines]
        labels = [line.getLegendLabel() for line in lines]

        scatters = [scatter for scatter in self.canvas().getScatters() if scatter.getLegendVisible() and scatter.getVisible()]
        objs.extend([self.__createLineFromScatter(scatter) for scatter in scatters])
        labels.extend([scatter.getLegendLabel() for scatter in scatters])

        kwargs = {}
        if self._pos is not None:
            kwargs["loc"] = "upper left"
            kwargs["bbox_to_anchor"] = (self._pos[0], 1 - self._pos[1])
        if self._family is not None:
            prop = FontInfo.getFontProperty(self._family)
            prop.set_size(self._size)
            kwargs["prop"] = prop
            kwargs["labelcolor"] = self._color
        if self._vis is not None:
            kwargs["frameon"] = self._vis
        leg = self.canvas().getAxes("BottomLeft").legend(objs, labels, **kwargs)
        if len(objs) == 0:
            leg.set_visible(False)
    
    def __createLineFromScatter(self, scatter):
        def get_relative_luminance(rgba):
            r, g, b, _ = rgba
            gamma_correct = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
            return (0.2126 * gamma_correct(r) + 0.7152 * gamma_correct(g) + 0.0722 * gamma_correct(b)) * 100
        
        def getColorFromColormap(cmap_name):
            cmap = pyplot.get_cmap(cmap_name)
            color = cmap(0.5)
            if get_relative_luminance(color) > 70:
                color = cmap(0.0) if get_relative_luminance(cmap(0.0)) < get_relative_luminance(cmap(1.0)) else cmap(1.0)
            return color

        markerstyle = self.__reverseMarkerMap[scatter.getMarker()]
        markercolor = getColorFromColormap(scatter.getColormap()) if scatter.getMarkerColorByData() else scatter.getMarkerColor()
        markersize = min(np.median(np.sqrt(scatter._marker.get_sizes())), self._size)

        linecolor = getColorFromColormap(scatter.getColormap()) if scatter.getLineColorByData() else scatter.getLineColor()
        linewidth = min(np.median(scatter._line.get_linewidths()), self._size)

        return lines.Line2D([0], [0], linestyle=scatter.getLineStyle(), linewidth=linewidth, color=linecolor, 
                      marker=markerstyle, markersize=markersize, markerfacecolor=markercolor, markeredgecolor=markercolor,
                      fillstyle=scatter.getMarkerFilling(), markeredgewidth=scatter.getMarkerThick())

    def _setLegendFont(self, font):
        self._family = font.fontName
        self._size = font.size
        self._color = font.color
        self.updateLegends()

    def _setLegendPosition(self, position):
        self._pos = position
        self.updateLegends()

    def _setLegendFrameVisible(self, visible):
        self._vis = visible
        self.updateLegends()
