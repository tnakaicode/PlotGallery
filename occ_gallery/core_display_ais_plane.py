#!/usr/bin/env python
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.AIS import AIS_ColorScale, AIS_Axis
from OCC.Core.Graphic3d import Graphic3d_ZLayerId_TopOSD, Graphic3d_TMF_2d
from OCC.Core.gp import gp_XY, gp_Pnt, gp_Dir, gp_Ax1
from OCC.Core.Geom import Geom_Line

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

myBox = BRepPrimAPI_MakeBox(60, 60, 50).Shape()

line = Geom_Line(gp_Ax1(gp_Pnt(-100, 0, 0), gp_Dir()))
axis = AIS_Axis(gp_Ax1())

display.Context.Display(axis, True)
display.DisplayShape(myBox, update=True)

start_display()