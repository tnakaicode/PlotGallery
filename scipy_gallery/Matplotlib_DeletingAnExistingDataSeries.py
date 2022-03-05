#!/usr/bin/env python
# coding: utf-8

# Matplotlib: deleting an existing data series
# ======================================================================
#
# Each axes instance contains a lines attribute, which is a list of the
# data series in the plot, added in chronological order. To delete a
# particular data series, one must simply delete the appropriate element
# of the lines list and redraw if necessary.
#
# The is illustrated in the following example from an interactive session:

import numpy as N
import matplotlib.pyplot as P

x = N.arange(10)

fig = P.figure()
ax = fig.add_subplot(111)
ax.plot(x)

ax.plot(x + 10)

ax.plot(x + 20)

P.show()
ax.lines

del ax.lines[1]
P.show()


# which will plot three lines, and then delete the second.
#
