#!/usr/bin/env python

# Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
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

from __future__ import print_function

from OCC.Core.gp import gp_Pnt, gp_Pln, gp_Trsf
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Extend.ShapeFactory import make_wire
from OCC.Core.TopLoc import TopLoc_Location

from OCC.Display.SimpleGui import init_display


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    dats = [
        # p1(x,y,z), p2(x,y,z), p3(x,y,z), radii, z
        [[0, 0], [5, 5], [-5, 5], 0.3, 0],
        [[0, 0], [5, 5], [-5, 5], 1.0, 1],
        [[0, 0], [5.1, 5], [-5, 5], 2.0, 2],
        [[0, 0], [5.0, 4.9], [-5, 5], 1.5, 3.5],
        [[0, 0], [5.1, 4.9], [-5.1, 5.1], 1.1, 4],
    ]

    api = BRepOffsetAPI_ThruSections()
    for data in dats:
        radius, z = data[3], data[4]
        # Defining the points
        p1 = gp_Pnt(*data[0], 0)
        p2 = gp_Pnt(*data[1], 0)
        p3 = gp_Pnt(*data[2], 0)

        # Making the edges
        ed1 = BRepBuilderAPI_MakeEdge(p3, p2).Edge()
        ed2 = BRepBuilderAPI_MakeEdge(p2, p1).Edge()

        # Making the 2dFillet
        f = ChFi2d_AnaFilletAlgo()
        f.Init(ed1, ed2, gp_Pln())
        f.Perform(radius)
        fillet2d = f.Result(ed1, ed2)

        trf = gp_Trsf()
        trf.SetTranslation(gp_Pnt(0, 0, 0), gp_Pnt(0, 0, z))

        # Create and display a wire
        w = make_wire([ed1, fillet2d, ed2])
        w.Location(TopLoc_Location(trf))
        display.DisplayShape(w)
        # display.DisplayMessage(p1, "p1")
        # display.DisplayMessage(p2, "p2")
        # display.DisplayMessage(p3, "p3")
        # display.DisplayShape(ed1)
        # display.DisplayShape(ed2)

        api.AddWire(w)
    api.Build()
    display.DisplayShape(api.Shape())

    display.FitAll()
    start_display()
