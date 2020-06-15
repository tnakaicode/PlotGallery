#!/usr/bin/env python
# coding: utf-8

# # Customising static orbit plots

# The default styling for plots works pretty well however sometimes you may need to change things. The following will show you how to change the style of your plots and have different types of lines and dots
#
# This is the default plot we will start with:


from astropy.time import Time
import matplotlib.pyplot as plt

from poliastro.plotting import StaticOrbitPlotter
from poliastro.frames import Planes
from poliastro.bodies import Earth, Mars, Jupiter, Sun
from poliastro.twobody import Orbit

dat = "2020-06-15 11:00:00"
epoch = Time(dat, scale="tdb")

fig, ax = plt.subplots()
ax.grid(True)
ax.set_title("Earth, Mars, and Jupiter")
ax.set_facecolor("None")

plotter = StaticOrbitPlotter(ax)
plotter.plot_body_orbit(Earth, epoch, label=Earth)
plotter.plot_body_orbit(Mars, epoch, label=Mars)
plotter.plot_body_orbit(Jupiter, epoch, label=Jupiter)
plt.savefig("./orbit.png")
plt.show()
