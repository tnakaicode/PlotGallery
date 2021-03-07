#!/usr/bin/env python
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

from OCC.Core.gp import gp_Pnt, gp_Pln, gp_Vec
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
from OCC.Core.ChFi3d import ChFi3d_Builder, ChFi3d_FilBuilder, ChFi3d_ChBuilder, ChFi3d_FilletShape
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCCUtils.Construct import make_plane

from OCC.Extend.ShapeFactory import make_wire

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_functionto_menu = init_display()

# Defining the points
p1 = gp_Pnt(0, 0, 0)
p2 = gp_Pnt(5, 5, 0)
p3 = gp_Pnt(-5, 5, 0)

# Making the edges
ed1 = BRepBuilderAPI_MakeEdge(p3, p2).Edge()
ed2 = BRepBuilderAPI_MakeEdge(p2, p1).Edge()

# Making the 2dFillet
f2 = ChFi2d_AnaFilletAlgo()
f2.Init(ed1, ed2, gp_Pln())
f2.Perform(1.0) # radius
fillet2d = f2.Result(ed1, ed2)

pln1 = make_plane(gp_Pnt(+200,0,0), gp_Vec(1,0,1))
pln2 = make_plane(gp_Pnt(-200,0,0), gp_Vec(-1,0,1))
f3 = ChFi3d_FilBuilder(pln1)

# Create and display a wire
w = make_wire([ed1, fillet2d, ed2])
#display.DisplayShape(w)
display.DisplayShape(ed1, color="BLUE")
display.DisplayShape(fillet2d)
display.DisplayShape(ed2, color="BLUE")
display.FitAll()
start_display()
