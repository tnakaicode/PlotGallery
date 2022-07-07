#!/usr/bin/env python
# coding: utf-8

from OCC.Display.SimpleGui import init_display

from math import pi

from OCC.Core.gp import gp_Pnt2d, gp_XOY, gp_Lin2d, gp_Ax3, gp_Dir2d
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_CylindricalSurface
from OCC.Core.GCE2d import GCE2d_MakeSegment


display, start_display, add_menu, add_function_to_menu = init_display()


# Build an helix
aCylinder = Geom_CylindricalSurface(gp_Ax3(gp_XOY()), 6.0)
aLine2d = gp_Lin2d (gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 1.0))
aSegment = GCE2d_MakeSegment(aLine2d, 0.0, pi * 2.0)

helix_edge = BRepBuilderAPI_MakeEdge(aSegment.Value(), aCylinder, 0.0, 6.0 * pi).Edge()


display.DisplayShape(helix_edge, update=True)
display.FitAll()
start_display()

