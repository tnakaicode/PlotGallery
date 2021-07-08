#!/usr/bin/env python
# coding: utf-8

# # PythonOCC - Example - Topology - Draft Angle

# Example of the ***BRepOffsetAPI_DraftAngle*** function allows modifying a shape by applying draft angles to its planar, cylindrical and conical faces.<br>

# imports from OCC.Core
import math
from OCC.Core.gp import gp_Dir, gp_Pln, gp_Ax3, gp_XOY
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_DraftAngle
from OCC.Core.Precision import precision_Angular
from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.Geom import Geom_Plane
from OCC.Core.TopoDS import topods_Face

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

# Generation of a box

S = BRepPrimAPI_MakeBox(20., 30., 15.).Shape()

# Apply a draft angle.

adraft = BRepOffsetAPI_DraftAngle(S)
topExp = TopExp_Explorer()
topExp.Init(S, TopAbs_FACE)
while topExp.More():
    face = topods_Face(topExp.Current())
    surf = Geom_Plane.DownCast(BRep_Tool_Surface(face))
    dirf = surf.Pln().Axis().Direction()
    ddd = gp_Dir(0, 0, 1)
    if dirf.IsNormal(ddd, precision_Angular()):
        adraft.Add(face, ddd, math.radians(15), gp_Pln(gp_Ax3(gp_XOY())))
    topExp.Next()
adraft.Build()
shp = adraft.Shape()


display.DisplayShape(S, transparency=0.9)
display.DisplayShape(shp)
start_display()
