#!/usr/bin/env python
# coding: utf-8

# Matplotlib: interactive plotting
# ======================================================================
#
# Interactive point identification
# --------------------------------
#
# I find it often quite useful to be able to identify points within a plot
# simply by clicking. This recipe provides a fairly simple
# [functor](http://en.wikipedia.org/wiki/Function_object) that can be
# connected to any plot. I've used it with both scatter and standard
# plots.
#
# Because often you'll have multiple views of a dataset spread across
# either multiple figures, or at least multiple axis, I've also provided a
# utility to link these plots together so clicking on a point in one plot
# will highlight and identify that data point on all other linked plots.


import numpy as np
import math
import matplotlib.pyplot as plt


class AnnoteFinder(object):
    """callback for matplotlib to display an annotation when points are
    clicked on.  The point which is closest to the click and within
    xtol and ytol is identified.

    Register this function like this:

    scatter(xdata, ydata)
    af = AnnoteFinder(xdata, ydata, annotes)
    connect('button_press_event', af)
    """

    def __init__(self, xdata, ydata, annotes, ax=None, xtol=None, ytol=None):
        self.data = list(zip(xdata, ydata, annotes))
        if xtol is None:
            xtol = ((max(xdata) - min(xdata)) / float(len(xdata))) / 2
        if ytol is None:
            ytol = ((max(ydata) - min(ydata)) / float(len(ydata))) / 2
        self.xtol = xtol
        self.ytol = ytol
        if ax is None:
            self.ax = plt.gca()
        else:
            self.ax = ax
        self.drawnAnnotations = {}
        self.links = []

    def distance(self, x1, x2, y1, y2):
        """
        return the distance between two points
        """
        return(math.sqrt((x1 - x2)**2 + (y1 - y2)**2))

    def __call__(self, event):

        if event.inaxes:

            clickX = event.xdata
            clickY = event.ydata
            if (self.ax is None) or (self.ax is event.inaxes):
                annotes = []
                # print(event.xdata, event.ydata)
                for x, y, a in self.data:
                    # print(x, y, a)
                    if ((clickX - self.xtol < x < clickX + self.xtol) and
                            (clickY - self.ytol < y < clickY + self.ytol)):
                        annotes.append(
                            (self.distance(x, clickX, y, clickY), x, y, a))
                if annotes:
                    annotes.sort()
                    distance, x, y, annote = annotes[0]
                    self.drawAnnote(event.inaxes, x, y, annote)
                    for l in self.links:
                        l.drawSpecificAnnote(annote)

    def drawAnnote(self, ax, x, y, annote):
        """
        Draw the annotation on the plot
        """
        if (x, y) in self.drawnAnnotations:
            markers = self.drawnAnnotations[(x, y)]
            for m in markers:
                m.set_visible(not m.get_visible())
            self.ax.figure.canvas.draw_idle()
        else:
            t = ax.text(x, y, " - %s" % (annote),)
            m = ax.scatter([x], [y], marker='d', c='r', zorder=100)
            self.drawnAnnotations[(x, y)] = (t, m)
            self.ax.figure.canvas.draw_idle()

    def drawSpecificAnnote(self, annote):
        annotesToDraw = [(x, y, a) for x, y, a in self.data if a == annote]
        for x, y, a in annotesToDraw:
            self.drawAnnote(self.ax, x, y, a)


# To use this functor you can simply do something like this:


x = range(10)
y = range(10)
annotes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']

fig, ax = plt.subplots()
ax.scatter(x, y)
af = AnnoteFinder(x, y, annotes, ax=ax)
fig.canvas.mpl_connect('button_press_event', af)


# This is fairly useful, but sometimes you'll have multiple views of a
# dataset and it is useful to click and identify a point in one plot and
# find it in another. The below code demonstrates this linkage and should
# work between multiple axis or figures.


def linkAnnotationFinders(afs):
    for i in range(len(afs)):
        allButSelfAfs = afs[:i] + afs[i + 1:]
        afs[i].links.extend(allButSelfAfs)


plt.figure()
plt.subplot(121)
plt.scatter(x, y)
af1 = AnnoteFinder(x, y, annotes)
plt.connect('button_press_event', af1)

plt.subplot(122)
plt.scatter(x, y)
af2 = AnnoteFinder(x, y, annotes)
plt.connect('button_press_event', af2)

linkAnnotationFinders([af1, af2])


# I find this fairly useful. By subclassing and redefining drawAnnote this
# simple framework could be used to drive a more sophisticated user
# interface.
#
# Currently this implementation is a little slow when the number of
# datapoints becomes large. I'm particularly interested in suggestions
# people might have for making this faster and better.
#
# * * * * *
#
# Handling click events while zoomed
# ==================================
#
# Often, you don't want to respond to click events while zooming or
# panning (selected using the toolbar mode buttons). You can avoid
# responding to those events by checking the attribute of the toolbar
# instance. The first example below shows how to do this using the pylab
# interface.


def click(event):
    """If the left mouse button is pressed: draw a little square. """
    tb = plt.get_current_fig_manager().toolbar
    if event.button == 1 and event.inaxes and tb.mode == '':
        x, y = event.xdata, event.ydata
        plt.plot([x], [y], 'rs')
        plt.draw()

plt.figure()
plt.plot((np.arange(100) / 99.0)**3)
plt.gca().set_autoscale_on(False)
plt.connect('button_press_event', click)
plt.show()


# If your application is in an wxPython window, then chances are you created a handle to the toolbar during setup, as shown in the {{{add_toolbar}}} method of the embedding_in_wx2.py example script, and can then access the {{{mode}}} attribute of that object (self.toolbar.mode in that case) in your click handling method.
