"""
===========
MathText WX
===========

Demonstrates how to convert mathtext to a wx.Bitmap for display in various
controls on wxPython.
"""

import matplotlib
matplotlib.use("WxAgg")
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure
import numpy as np

import wx

IS_GTK = 'wxGTK' in wx.PlatformInfo
IS_WIN = 'wxMSW' in wx.PlatformInfo

############################################################
# This is where the "magic" happens.
from matplotlib.mathtext import MathTextParser
mathtext_parser = MathTextParser("Bitmap")


def mathtext_to_wxbitmap(s):
    rgba, depth = mathtext_parser.to_rgba(s, dpi=150, fontsize=10)
    return wx.Bitmap.FromBufferRGBA(rgba.shape[1], rgba.shape[0], rgba)
############################################################

functions = [
    (r'$\sin(2 \pi x)$', lambda x: np.sin(2*np.pi*x)),
    (r'$\frac{4}{3}\pi x^3$', lambda x: (4.0/3.0)*np.pi*x**3),
    (r'$\cos(2 \pi x)$', lambda x: np.cos(2*np.pi*x)),
    (r'$\log(x)$', lambda x: np.log(x))
]


class CanvasFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title, size=(550, 350))

        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)

        self.canvas = FigureCanvas(self, -1, self.figure)

        self.change_plot(0)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.add_buttonbar()
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.GROW)
        self.add_toolbar()  # comment this out for no toolbar

        menuBar = wx.MenuBar()

        # File Menu
        menu = wx.Menu()
        m_exit = menu.Append(
            wx.ID_EXIT, "E&xit\tAlt-X", "Exit this simple sample")
        menuBar.Append(menu, "&File")
        self.Bind(wx.EVT_MENU, self.OnClose, m_exit)

        if IS_GTK or IS_WIN:
            # Equation Menu
            menu = wx.Menu()
            for i, (mt, func) in enumerate(functions):
                bm = mathtext_to_wxbitmap(mt)
                item = wx.MenuItem(menu, 1000 + i, " ")
                item.SetBitmap(bm)
                menu.Append(item)
                self.Bind(wx.EVT_MENU, self.OnChangePlot, item)
            menuBar.Append(menu, "&Functions")

        self.SetMenuBar(menuBar)

        self.SetSizer(self.sizer)
        self.Fit()

    def add_buttonbar(self):
        self.button_bar = wx.Panel(self)
        self.button_bar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.button_bar, 0, wx.LEFT | wx.TOP | wx.GROW)

        for i, (mt, func) in enumerate(functions):
            bm = mathtext_to_wxbitmap(mt)
            button = wx.BitmapButton(self.button_bar, 1000 + i, bm)
            self.button_bar_sizer.Add(button, 1, wx.GROW)
            self.Bind(wx.EVT_BUTTON, self.OnChangePlot, button)

        self.button_bar.SetSizer(self.button_bar_sizer)

    def add_toolbar(self):
        """Copied verbatim from embedding_wx2.py"""
        self.toolbar = NavigationToolbar2Wx(self.canvas)
        self.toolbar.Realize()
        # By adding toolbar in sizer, we are able to put it at the bottom
        # of the frame - so appearance is closer to GTK version.
        self.sizer.Add(self.toolbar, 0, wx.LEFT | wx.EXPAND)
        # update the axes menu on the toolbar
        self.toolbar.update()

    def OnChangePlot(self, event):
        self.change_plot(event.GetId() - 1000)

    def change_plot(self, plot_number):
        t = np.arange(1.0, 3.0, 0.01)
        s = functions[plot_number][1](t)
        self.axes.clear()
        self.axes.plot(t, s)
        self.canvas.draw()

    def OnClose(self, event):
        self.Destroy()


class MyApp(wx.App):
    def OnInit(self):
        frame = CanvasFrame(None, "wxPython mathtext demo app")
        self.SetTopWindow(frame)
        frame.Show(True)
        return True


if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
