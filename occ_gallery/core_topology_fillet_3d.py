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
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax1, gp_Trsf
from OCC.Core.LocOpe import LocOpe_FindEdges
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCCUtils.Construct import make_box

display, start_display, add_menu, add_function_to_menu = init_display()

box1 = make_box(gp_Pnt(0, 0, 0), 20, 20, 20)
box1_faces = list(TopologyExplorer(box1).faces())

# Make Shell by only two faces
box1_shell = TopoDS_Shell()
bild = BRep_Builder()
bild.MakeShell(box1_shell)
for shp in [box1_faces[0], box1_faces[2]]:
    bild.Add(box1_shell, shp)

# Find Edge that the two faces share
find_edge = LocOpe_FindEdges(box1_faces[0], box1_faces[2])
find_edge.InitIterator()
fillet_edge = find_edge.EdgeTo()

# Create Fillet of R5 on shared Edge.
fillet = BRepFilletAPI_MakeFillet(box1_shell, 0)
fillet.Add(5, fillet_edge)
fillet.Build()
if fillet.IsDone():
    display.DisplayShape(fillet.Shape())
else:
    print("fillet is not done")
display.DisplayShape(box1_shell, transparency=0.7)

box2 = make_box(gp_Pnt(40, 0, 0), 20, 20, 20)
box2_faces = list(TopologyExplorer(box2).faces())

# Rotate 0 degree
box2_trsf = gp_Trsf()
box2_trsf.SetRotation(gp_Ax1(gp_Pnt(40, 0, 0), gp_Dir(0, 0, 1)),
                      np.deg2rad(30))
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

display.DisplayShape(box2_shell, transparency=0.7)

display.FitAll()
start_display()

# MakeFillet between 2 faces is Failure
#
# 共有辺を持つ2面の間にFilletを作ろうとしたところ、fillet.Build()の段階で失敗した。
# 以下のコードでは、MakeBoxで作ったboxから辺を共有する2面を取り出してFilletを作っている。
# box1では成功するが、面の位置を変えす(0度回転)明らかに共有する辺があるのにbox2では失敗する。
# When I tried to create a Fillet between two faces with shared edges, it failed at the fillet.Build() stage.
# In my code below, Fillet is created by taking 2 faces that share an edge from a box created by MakeBox.
# It succeeds in box1, but fails in box2 when the faces are repositioned (rotated 0 degrees) and there are clearly shared edges.
#

# 私は辺を共有するどんな2面でもFilletが作れないかと検討しています。
# あなたの解決策は、2面をつくるためのBox全体を回転させているため、Box1とおなじ状態と言えます。
# 例えば、最初のコードの回転を30度に変えた場合の2面のFilletを作る方法はないでしょうか？
# I am considering the possibility of creating a Fillet with any 2 sides that share an edge.
# Your solution is the same situation as Box1 because you are rotating the entire Box to create the 2 sides.
# Is there any way to create a Fillet with 2 sides if, for example, I change the rotation of the first code to 30 degrees?
