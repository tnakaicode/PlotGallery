#!/usr/bin/env python
# coding: utf-8

# # PythonOCC - Example - Topology - Make Prism

# Example of the ***BRepPrimAPI_MakePrism*** function building linear swept topologies, called prisms.<br>
# In this example, the prism is defined by a bspline edge which is swept along a vector.
# The result is a face.


# imports from OCC.Core
from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.BRepSweep import BRepSweep_Prism

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

# the bspline profile
array = TColgp_Array1OfPnt(1, 5)
array.SetValue(1, gp_Pnt(0, 0, 0))
array.SetValue(2, gp_Pnt(1, 2, 0))
array.SetValue(3, gp_Pnt(2, 3, 0))
array.SetValue(4, gp_Pnt(4, 3, 0))
array.SetValue(5, gp_Pnt(5, 5, 0))
bspline = GeomAPI_PointsToBSpline(array).Curve()
profile = BRepBuilderAPI_MakeEdge(bspline).Edge()


# Generation of the linear path.


# the linear path
starting_point = gp_Pnt(0.0, 0.0, 0.0)
end_point = gp_Pnt(0.0, 0.0, 6.0)
vec = gp_Vec(starting_point, end_point)
path = BRepBuilderAPI_MakeEdge(starting_point, end_point).Edge()


# Build the prism model resulting from the bspline extrusion allong the linear path


prism = BRepPrimAPI_MakePrism(profile, vec).Shape()
display.DisplayShape(prism, color="BLUE1")

sweep = BRepSweep_Prism(prism, gp_Vec(1, 1, 0)).Shape()
display.DisplayShape(sweep)

display.FitAll()
start_display()
