"""
=============
Span Selector
=============

The SpanSelector is a mouse widget to select a xmin/xmax range and plot the
detail view of the selected region in the lower axes
"""

"""
Widgets class list
class LockDraw(object):
class Widget(object):
class AxesWidget(Widget):
class Button(AxesWidget):
class Slider(AxesWidget):
class CheckButtons(AxesWidget):
class TextBox(AxesWidget):
class RadioButtons(AxesWidget):
class SubplotTool(Widget):
class Cursor(AxesWidget):
class MultiCursor(Widget):
class _SelectorWidget(AxesWidget):
class SpanSelector(_SelectorWidget):
class ToolHandles(object):
class RectangleSelector(_SelectorWidget):
class EllipseSelector(RectangleSelector):
class LassoSelector(_SelectorWidget):
class PolygonSelector(_SelectorWidget):
class Lasso(AxesWidget):
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector

# Fixing random state for reproducibility
np.random.seed(19680801)

fig, (ax1, ax2) = plt.subplots(2, figsize=(8, 6))
ax1.set(facecolor='#FFFFCC')

x = np.arange(0.0, 1.0, 0.001) * 2.5 * np.pi
y = np.sin(x) + 0.1 * np.random.randn(len(x))

ax1.plot(x, y, '-')
ax1.plot(x, np.sin(x))
ax1.set_ylim(-2, 2)
ax1.set_title('Press left mouse button and drag to test')

ax2.set(facecolor='#FFFFCC')
line2, = ax2.plot(x, y, '-')


def onselect(xmin, xmax):
    indmin, indmax = np.searchsorted(x, (xmin, xmax))
    indmax = min(len(x) - 1, indmax)

    thisx = x[indmin:indmax]
    thisy = y[indmin:indmax]
    line2.set_data(thisx, thisy)
    ax2.set_xlim(thisx[0], thisx[-1])
    ax2.set_ylim(thisy.min(), thisy.max())
    fig.canvas.draw()

#############################################################################
# .. note::
#
#    If the SpanSelector object is garbage collected you will lose the
#    interactivity.  You must keep a hard reference to it to prevent this.
#


span = SpanSelector(ax1, onselect, 'horizontal', useblit=True,
                    rectprops=dict(alpha=0.5, facecolor='red'))
# Set useblit=True on most backends for enhanced performance.


plt.show()
