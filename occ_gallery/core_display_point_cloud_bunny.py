#!/usr/bin/env python

# Copyright 2016 Thomas Paviot (tpaviot@gmail.com)
##
# This file is part of pythonOCC.
##
# pythonOCC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# pythonOCC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np

from OCC.Core.gp import gp_Pnt
from OCCUtils.Construct import make_polygon

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

from scipy.spatial import ConvexHull, Delaunay, voronoi_plot_2d

pcd_file = "./models/bunny.pcd"
dat = np.loadtxt(pcd_file, skiprows=10)

cov = Delaunay(dat[:, 0:2])
print(cov.simplices)
# print(cov.vertices)

for xyz in dat:
    display.DisplayShape(gp_Pnt(*xyz))

for ixyz in cov.simplices:
    lxyz = dat[ixyz]
    display.DisplayShape(make_polygon(gp_Pnt(*p) for p in lxyz))

display.FitAll()
start_display()
