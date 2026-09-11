import unittest
import shutil
import os
import warnings

import numpy as np

from lys import glb, home, Wave, display, errors, filters


class Graph_test(unittest.TestCase):
    path = "test/DataFiles"

    def setUp(self):
        warnings.simplefilter("ignore", errors.NotSupportedWarning)
        if glb.mainWindow() is None:
            if os.path.exists(home() + "/.lys"):
                shutil.rmtree(home() + "/.lys")
            glb.createMainWindow(show=False, restore=True)
        self.graphs = [display(lib=lib) for lib in ["matplotlib", "pyqtgraph"]]
        #self.graphs = [Graph(lib=lib) for lib in ["matplotlib"]]

    def test_CanvasData(self):
        for g in self.graphs:
            d = {}
            c = g.canvas

            is_matplotlib = "MatplotLib" in str(c.__class__)

            # append data
            data1d = Wave([1, 2, 3])
            data2d = Wave([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
            data2dc = Wave([[1 + 1j, 2 + 2j], [3 + 3j, 4 + 4j]])
            line = c.Append(data1d)
            line2 = c.Append(data1d, axis="TopRight")
            image = c.Append(data2d)
            cont = c.Append(data2d, contour=True)
            rgb = c.Append(data2dc)
            if is_matplotlib:
                scatter = c.Append(data1d, scatter=True)
                scatter2 = c.Append(data1d, axis="TopRight", scatter=True)
                vec = c.Append(data2dc, vector=True)

            # get wave data
            self.assertEqual(len(c.getLines()), 2)
            self.assertEqual(len(c.getImages()), 1)
            self.assertEqual(len(c.getContours()), 1)
            self.assertEqual(len(c.getRGBs()), 1)
            if is_matplotlib:
                self.assertEqual(len(c.getScatters()), 2)
                self.assertEqual(len(c.getVectorFields()), 1)

            c.SaveAsDictionary(d)

            # remove
            c.Remove(line)
            c.Remove(image)
            c.Remove(cont)
            c.Remove(rgb)
            if is_matplotlib:
                c.Remove(vec)
                c.Remove(scatter)

            self.assertEqual(len(c.getLines()), 1)
            self.assertEqual(len(c.getImages()), 0)
            self.assertEqual(len(c.getContours()), 0)
            self.assertEqual(len(c.getRGBs()), 0)
            if is_matplotlib:
                self.assertEqual(len(c.getScatters()), 1)
                self.assertEqual(len(c.getVectorFields()), 0)

            # load
            c.LoadFromDictionary(d)
            self.assertEqual(len(c.getLines()), 2)
            self.assertEqual(len(c.getImages()), 1)
            self.assertEqual(len(c.getContours()), 1)
            self.assertEqual(len(c.getRGBs()), 1)
            if is_matplotlib:
                self.assertEqual(len(c.getScatters()), 2)
                self.assertEqual(len(c.getVectorFields()), 1)
            
            c.Clear()
            self.assertEqual(len(c.getWaveData()), 0)

    def test_WaveData(self):
        for g in self.graphs:
            c = g.canvas

            line = c.Append(Wave([1, 2, 3]))
            line.setVisible(False)
            self.assertFalse(line.getVisible())

            line.setOffset((1, 1, 2, 2))
            self.assertEqual(line.getOffset(), (1, 1, 2, 2))

            f = filters.SimpleMathFilter('+', 1)
            line.setFilter(f)
            self.assertEqual(line.getFilter(), f)

            line.setZOrder(11)
            self.assertEqual(line.getZOrder(), 11)

    def test_Line(self):
        for g in self.graphs:
            c = g.canvas

            line = c.Append(Wave([1, 2, 3]))
            line.setColor('#ff0000')
            self.assertEqual(line.getColor(), '#ff0000')

            line.setWidth(3)
            self.assertEqual(line.getWidth(), 3)

            line.setStyle("dashed")
            self.assertEqual(line.getStyle(), 'dashed')

            line.setMarker('circle')
            self.assertEqual(line.getMarker(), 'circle')

            line.setMarkerSize(5)
            self.assertEqual(line.getMarkerSize(), 5)

            line.setMarkerThick(3)
            self.assertEqual(line.getMarkerThick(), 3)

            line.setMarkerFilling('full')
            self.assertEqual(line.getMarkerFilling(), 'full')

            line.setErrorbar(4, direction="y")
            line.setErrorbar(3, direction="x")
            self.assertEqual(line.getErrorbar("y"), 4)
            self.assertEqual(line.getErrorbar("x"), 3)

            line.setCapSize(3)
            self.assertEqual(line.getCapSize(), 3)

            line.setLegendVisible(True)
            self.assertTrue(line.getLegendVisible())

            line.setLegendLabel("test")
            self.assertEqual(line.getLegendLabel(), "test")

            ap = line.saveAppearance()
            line.setColor('#ff00ff')
            line.setWidth(4)
            line.setStyle("solid")
            line.setMarker('nothing')
            line.setMarkerSize(3)
            line.setMarkerThick(2)
            line.setMarkerFilling('none')
            line.setErrorbar(5, direction="y")
            line.setCapSize(2)
            line.setLegendVisible(False)
            line.setLegendLabel("aaa")

            line.loadAppearance(ap)
            self.assertEqual(line.getWidth(), 3)
            self.assertEqual(line.getStyle(), 'dashed')
            self.assertEqual(line.getMarker(), 'circle')
            self.assertEqual(line.getMarkerSize(), 5)
            self.assertEqual(line.getMarkerThick(), 3)
            self.assertEqual(line.getMarkerFilling(), 'full')
            self.assertEqual(line.getErrorbar("y"), 4)
            self.assertEqual(line.getCapSize(), 3)
            self.assertTrue(line.getLegendVisible())
            self.assertEqual(line.getLegendLabel(), "test")

    def test_Image(self):
        for g in self.graphs:
            c = g.canvas

            im = c.Append(Wave([[1, 2, 3], [4, 5, 6]]))
            im.setColormap('bwr')
            self.assertEqual(im.getColormap(), 'bwr')

            im.setGamma(0.5)
            self.assertEqual(im.getGamma(), 0.5)

            im.setOpacity(0.7)
            self.assertEqual(im.getOpacity(), 0.7)

            im.setColorRange(1, 3)
            self.assertEqual(im.getColorRange(), (1, 3))

            im.setLog(True)
            self.assertTrue(im.isLog())

            ap = im.saveAppearance()
            im.setColormap('gray')
            im.setGamma(0.4)
            im.setOpacity(0.6)
            im.setColorRange(2, 4)
            im.setLog(False)

            im.loadAppearance(ap)
            self.assertEqual(im.getColormap(), 'bwr')
            self.assertEqual(im.getGamma(), 0.5)
            self.assertEqual(im.getOpacity(), 0.7)
            self.assertEqual(im.getColorRange(), (1, 3))
            self.assertTrue(im.isLog())

    def test_RGB(self):
        for g in self.graphs:
            c = g.canvas

            im = c.Append(Wave([[1 + 1j, 2, 3], [4, 5, 6]]))
            im.setColorRotation(99)
            self.assertEqual(im.getColorRotation(), 99)

            im.setColorRange(0, 5)
            self.assertEqual(im.getColorRange(), (0, 5))

            ap = im.saveAppearance()
            im.setColorRotation(9)
            im.setColorRange(0, 2)

            im.loadAppearance(ap)
            self.assertEqual(im.getColorRotation(), 99)
            self.assertEqual(im.getColorRange(), (0, 5))

    def test_Vector(self):
        for g in [self.graphs[0]]:
            c = g.canvas

            v = c.Append(Wave([[1 + 1j, 2, 3], [4, 5, 6]]), vector=True)
            v.setWidth(3)
            self.assertEqual(v.getWidth(), 3)

            v.setScale(4)
            self.assertEqual(v.getScale(), 4)

            v.setPivot('tail')
            self.assertEqual(v.getPivot(), 'tail')

            v.setColor('#ff0000')
            self.assertEqual(v.getColor(), '#ff0000')

            ap = v.saveAppearance()
            v.setWidth(5)
            v.setScale(6)
            v.setPivot('middle')
            v.setColor('#ff00ff')

            v.loadAppearance(ap)
            self.assertEqual(v.getWidth(), 3)
            self.assertEqual(v.getScale(), 4)
            self.assertEqual(v.getPivot(), 'tail')
            self.assertEqual(v.getColor(), '#ff0000')

    def test_Contour(self):
        for g in self.graphs:
            c = g.canvas

            line = c.Append(Wave(np.random.rand(100, 100)), contour=True)
            line.setLevel(0.5)
            self.assertEqual(line.getLevel(), 0.5)

            line.setColor('#ff0000')
            self.assertEqual(line.getColor(), '#ff0000')

            line.setWidth(3)
            self.assertEqual(line.getWidth(), 3)

            line.setStyle("dashed")
            self.assertEqual(line.getStyle(), 'dashed')

            ap = line.saveAppearance()
            line.setLevel(0.4)
            line.setColor('#ff00ff')
            line.setWidth(4)
            line.setStyle("solid")

            line.loadAppearance(ap)
            self.assertEqual(line.getLevel(), 0.5)
            self.assertEqual(line.getColor(), '#ff0000')
            self.assertEqual(line.getWidth(), 3)
            self.assertEqual(line.getStyle(), 'dashed')

    def test_Scatter(self):
        for g in [self.graphs[0]]:
            c = g.canvas

            scatter = c.Append(Wave([1, 2, 3]), scatter=True)

            scatter.setColormap('bwr')
            self.assertEqual(scatter.getColormap(), 'bwr')

            scatter.setGamma(0.5)
            self.assertEqual(scatter.getGamma(), 0.5)

            scatter.setOpacity(0.7)
            self.assertEqual(scatter.getOpacity(), 0.7)

            scatter.setColorRange(1, 3)
            self.assertEqual(scatter.getColorRange(), (1, 3))

            scatter.setLog(True)
            self.assertTrue(scatter.isLog())

            scatter.setMarkerSizeByData(True)
            self.assertTrue(scatter.getMarkerSizeByData())

            scatter.setMarkerColorByData(True)
            self.assertTrue(scatter.getMarkerColorByData())

            scatter.setMarkerSizeExpression("2*z+1")
            self.assertEqual(scatter.getMarkerSizeExpression(), "2*z+1")

            scatter.setMarker('circle')
            self.assertEqual(scatter.getMarker(), 'circle')

            scatter.setMarkerSize(5)
            self.assertEqual(scatter.getMarkerSize(), 5)

            scatter.setMarkerThick(3)
            self.assertEqual(scatter.getMarkerThick(), 3)

            scatter.setMarkerFilling('full')
            self.assertEqual(scatter.getMarkerFilling(), 'full')

            scatter.setMarkerColor('#ff0000')
            self.assertEqual(scatter.getMarkerColor(), '#ff0000')

            scatter.setMarkerOpacity(0.8)
            self.assertEqual(scatter.getMarkerOpacity(), 0.8)

            scatter.setLineColorByData(True)
            self.assertTrue(scatter.getLineColorByData())

            scatter.setLineWidthByData(True)
            self.assertTrue(scatter.getLineWidthByData())

            scatter.setLineWidthExpression("-z-1")
            self.assertEqual(scatter.getLineWidthExpression(), "-z-1")

            scatter.setLineStyle('solid')
            self.assertEqual(scatter.getLineStyle(), 'solid')

            scatter.setLineWidth(2)
            self.assertEqual(scatter.getLineWidth(), 2)

            scatter.setLineColor('#00ff00')
            self.assertEqual(scatter.getLineColor(), '#00ff00')

            scatter.setLineOpacity(0.8)
            self.assertEqual(scatter.getLineOpacity(), 0.8)

            scatter.setErrorbar(4, direction="y")
            scatter.setErrorbar(3, direction="x")
            self.assertEqual(scatter.getErrorbar("y"), 4)
            self.assertEqual(scatter.getErrorbar("x"), 3)

            scatter.setCapSize(3)
            self.assertEqual(scatter.getCapSize(), 3)

            scatter.setLegendVisible(True)
            self.assertTrue(scatter.getLegendVisible())

            scatter.setLegendLabel("test")
            self.assertEqual(scatter.getLegendLabel(), "test")

            ap = scatter.saveAppearance()
            scatter.setColormap('gray')
            scatter.setGamma(0.4)
            scatter.setOpacity(0.6)
            scatter.setColorRange(2, 4)
            scatter.setLog(False)

            scatter.setMarkerSizeByData(False)
            scatter.setMarkerColorByData(False)
            scatter.setMarkerSizeExpression("5*z-8")
            scatter.setMarker('nothing')
            scatter.setMarkerSize(3)
            scatter.setMarkerThick(2)
            scatter.setMarkerFilling('none')
            scatter.setMarkerColor('#0000ff')
            scatter.setMarkerOpacity(0.6)

            scatter.setLineColorByData(False)
            scatter.setLineWidthByData(False)
            scatter.setLineWidthExpression("z+8")
            scatter.setLineStyle('none')
            scatter.setLineWidth(5)
            scatter.setLineColor('#ff0000')
            scatter.setLineOpacity(0.4)

            scatter.setErrorbar(5, direction="y")
            scatter.setCapSize(2)
            scatter.setLegendVisible(False)
            scatter.setLegendLabel("aaa")

            scatter.loadAppearance(ap)
            self.assertEqual(scatter.getColormap(), 'bwr')
            self.assertEqual(scatter.getGamma(), 0.5)
            self.assertEqual(scatter.getOpacity(), 0.7)
            self.assertEqual(scatter.getColorRange(), (1, 3))
            self.assertTrue(scatter.isLog())

            self.assertTrue(scatter.getMarkerSizeByData())
            self.assertTrue(scatter.getMarkerColorByData())
            self.assertEqual(scatter.getMarkerSizeExpression(), "2*z+1")
            self.assertEqual(scatter.getMarker(), 'circle')
            self.assertEqual(scatter.getMarkerSize(), 5)
            self.assertEqual(scatter.getMarkerThick(), 3)
            self.assertEqual(scatter.getMarkerFilling(), 'full')
            self.assertEqual(scatter.getMarkerColor(), '#ff0000')
            self.assertEqual(scatter.getMarkerOpacity(), 0.8)

            self.assertTrue(scatter.getLineColorByData())
            self.assertTrue(scatter.getLineWidthByData())
            self.assertEqual(scatter.getLineWidthExpression(), "-z-1")
            self.assertEqual(scatter.getLineStyle(), 'solid')
            self.assertEqual(scatter.getLineWidth(), 2)
            self.assertEqual(scatter.getLineColor(), '#00ff00')
            self.assertEqual(scatter.getLineOpacity(), 0.8)

            self.assertEqual(scatter.getErrorbar("y"), 4)
            self.assertEqual(scatter.getCapSize(), 3)
            self.assertTrue(scatter.getLegendVisible())
            self.assertEqual(scatter.getLegendLabel(), "test")

