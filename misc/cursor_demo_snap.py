"""
===========
Cursor Demo
===========

This example shows how to use Matplotlib to provide a data cursor.  It uses
Matplotlib to draw the cursor and may be a slow since this requires redrawing
the figure with every mouse move.

Faster cursoring is possible using native GUI drawing, as in
:doc:`/gallery/user_interfaces/wxcursor_demo_sgskip`.

The mpldatacursor__ and mplcursors__ third-party packages can be used to
achieve a similar effect.

__ https://github.com/joferkington/mpldatacursor
__ https://github.com/anntzer/mplcursors
"""

import matplotlib.pyplot as plt
import numpy as np


class SnaptoCursor(object):
    """
    Like Cursor but the crosshair snaps to the nearest x, y point.
    For simplicity, this assumes that *x* is sorted.
    """

    def __init__(self, x, y):
        self.fig, self.axs = plt.subplots()
        self.l1, = self.axs.plot(x, y)
        self.l2, = self.axs.plot(2 * x, y)
        self.lx = self.axs.axhline(color='k')  # the horiz line
        self.ly = self.axs.axvline(color='k')  # the vert line
        self.x = x
        self.y = y
        # text location in axes coords
        self.txt = self.axs.text(0.7, 0.9, '', transform=self.axs.transAxes)

    def mouse_move(self, event):
        if not event.inaxes:
            return

        x, y = event.xdata, event.ydata
        ln_xdata = self.l1._x
        ln_ydata = self.l1._y
        indx = min(np.searchsorted(ln_xdata, x), ln_xdata.shape[0])
        x = self.x[indx]
        y = self.y[indx]
        # update the line positions
        self.lx.set_ydata(y)
        self.ly.set_xdata(x)

        self.txt.set_text('x=%1.2f, y=%1.2f' % (x, y))
        print('x=%1.2f, y=%1.2f' % (x, y))
        self.axs.figure.canvas.draw()


t = np.linspace(-1, 1, 200) * np.pi
s = np.sin(2 * t)

cursor = SnaptoCursor(t, s)
#cursor.fig.canvas.mpl_connect('motion_notify_event', cursor.mouse_move)
cursor.fig.canvas.mpl_connect('button_press_event', cursor.mouse_move)
plt.show()
