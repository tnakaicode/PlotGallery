# Copyright 2009-2016 Thomas Paviot (tpaviot@gmail.com)
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
import sys
import numpy as np
from math import cos, pi

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax1, gp_Trsf, gp_Vec
from OCC.Core.LocOpe import LocOpe_FindEdges
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCCUtils.Construct import make_box, make_plane

display, start_display, add_menu, add_function_to_menu = init_display()


def split_box(box, plns):
    splitter = BOPAlgo_Splitter()
    splitter.AddArgument(box)
    for p in plns:
        splitter.AddTool(p)
    splitter.Perform()

    shps = []
    exp = TopExp_Explorer(splitter.Shape(), TopAbs_SOLID)
    while exp.More():
        shps.append(exp.Current())
        exp.Next()
    return shps


pln1 = make_plane(gp_Pnt(0, 0, 50),
                  gp_Vec(0, 0.5, 0.8),
                  -1000, 1000, -1000, 1000)

pln2 = make_plane(gp_Pnt(50, 0, 0),
                  gp_Vec(0.5, 0.0, 0.5),
                  -1000, 1000, -1000, 1000)
pln = [pln1, pln2]

box1 = make_box(gp_Pnt(0, 0, 0), 100, 100, 100)
box1 = split_box(box1, pln)[0]
box1_faces = list(TopologyExplorer(box1).faces())

# Make Shell by only two faces
box1_shell = TopoDS_Shell()
bild = BRep_Builder()
bild.MakeShell(box1_shell)
for shp in [box1_faces[4], box1_faces[2], box1_faces[3]]:
    bild.Add(box1_shell, shp)

# Find Edge that the two faces share
find_edge = LocOpe_FindEdges(box1_faces[4], box1_faces[2])
find_edge.InitIterator()
fillet_edge = find_edge.EdgeTo()

# Create Fillet of R5 on shared Edge.
fillet = BRepFilletAPI_MakeFillet(box1_shell, 0)
fillet.Add(10.0, fillet_edge)
fillet.Build()
if fillet.IsDone():
    display.DisplayShape(fillet.Shape())
else:
    print("fillet is not done")
display.DisplayShape(box1, transparency=0.7)
display.DisplayShape(fillet_edge, color="BLUE1")
display.DisplayShape(box1_shell, transparency=0.7, color="RED")

box2 = make_box(gp_Pnt(110, 0, 0), 20, 20, 20)
box2 = split_box(box2, pln)[0]
box2_faces = list(TopologyExplorer(box2).faces())

# Rotate 0 degree
box2_trsf = gp_Trsf()
box2_trsf.SetRotation(gp_Ax1(gp_Pnt(40, 0, 0), gp_Dir(0, 0, 1)), np.deg2rad(0))
box2_faces[0].Move(TopLoc_Location(box2_trsf))

# Make Shell by only two faces
box2_shell = TopoDS_Shell()
bild = BRep_Builder()
bild.MakeShell(box2_shell)
for shp in [box2_faces[0], box2_faces[2]]:
    bild.Add(box2_shell, shp)

# Find Edge that the two faces share
find_edge = LocOpe_FindEdges(box2_faces[0], box2_faces[2])
find_edge.InitIterator()
fillet_edge = find_edge.EdgeTo()

# Create Fillet of R5 on shared Edge.
fillet = BRepFilletAPI_MakeFillet(box2_shell, 0)
fillet.Add(5, fillet_edge)
# fillet.Build()
# RuntimeError: Standard_Failure There are no suitable edges for chamfer or fillet raised from method Build of class BRepBuilderAPI_MakeShape
if fillet.IsDone():
    display.DisplayShape(fillet.Shape())
else:
    print("fillet is not done")

display.DisplayShape(box2, transparency=0.7)
display.DisplayShape(fillet_edge, color="BLUE1")
display.DisplayShape(box2_shell, transparency=0.7, color="RED")

display.FitAll()
start_display()
