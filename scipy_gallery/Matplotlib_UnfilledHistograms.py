#!/usr/bin/env python
# coding: utf-8

# Matplotlib: unfilled histograms
# ======================================================================
#
# Here's some template code for plotting histograms that don't look like
# bar charts, but instead have only outlines (like IDL creates).
#
# First define a function that does the bulk of the heavy lifting.


import numpy as np
import matplotlib.pyplot as plt


def histOutline(dataIn, *args, **kwargs):
    (histIn, binsIn) = np.histogram(dataIn, *args, **kwargs)

    stepSize = binsIn[1] - binsIn[0]

    bins = np.zeros(len(binsIn) * 2 + 2, dtype=np.float)
    data = np.zeros(len(binsIn) * 2 + 2, dtype=np.float)
    for bb in range(len(binsIn)):
        bins[2 * bb + 1] = binsIn[bb]
        bins[2 * bb + 2] = binsIn[bb] + stepSize
        if bb < len(histIn):
            data[2 * bb + 1] = histIn[bb]
            data[2 * bb + 2] = histIn[bb]

    bins[0] = bins[1]
    bins[-1] = bins[-2]
    data[0] = 0
    data[-1] = 0

    return (bins, data)


# Now we can make plots:


# Make some data to plot
data = np.random.randn(500)

plt.figure(2, figsize=(10, 5))

##########
#
# First make a normal histogram
#
##########
plt.subplot(1, 2, 1)
(n, bins, patches) = plt.hist(data)

# Boundaries
xlo = -max(abs(bins))
xhi = max(abs(bins))
ylo = 0
yhi = max(n) * 1.1

plt.axis([xlo, xhi, ylo, yhi])

##########
#
# Now make a histogram in outline format
#
##########
(bins, n) = histOutline(data)

plt.subplot(1, 2, 2)
plt.plot(bins, n, 'k-')
plt.axis([xlo, xhi, ylo, yhi])

plt.show()

# Below you can find this functionality packaged up into histOutline.py
