#!/usr/bin/env python
# coding: utf-8

# Matplotlib: thick axes
# ======================================================================
#
# Example of how to thicken the lines around your plot (axes lines) and to
# get big bold fonts on the tick and axis labels.

import matplotlib.pyplot as plt

# Thicken the axes lines and labels
#
#   Comment by J. R. Lu:
#       I couldn't figure out a way to do this on the
#       individual plot and have it work with all backends
#       and in interactive mode. So, used rc instead.
#
plt.rc('axes', linewidth=2)

# Make a dummy plot
plt.plot([0, 1], [0, 1])

# Change size and font of tick labels
# Again, this doesn't work in interactive mode.
fontsize = 14
ax = plt.gca()

for tick in ax.xaxis.get_major_ticks():
    tick.label1.set_fontsize(fontsize)
    tick.label1.set_fontweight('bold')
for tick in ax.yaxis.get_major_ticks():
    tick.label1.set_fontsize(fontsize)
    tick.label1.set_fontweight('bold')

plt.xlabel('X Axis', fontsize=16, fontweight='bold')
plt.ylabel('Y Axis', fontsize=16, fontweight='bold')

# Save figure
plt.savefig('thick_axes.png')
plt.show()
