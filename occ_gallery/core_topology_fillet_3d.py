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
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.TopoDS import TopoDS_Shell
from OCC.Display.SimpleGui import init_display
from OCC.Core.TColgp import TColgp_Array1OfPnt2d
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir, gp_Pnt2d, gp_Ax1, gp_Trsf
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCCUtils.Construct import make_box

display, start_display, add_menu, add_function_to_menu = init_display()

box1 = make_box(gp_Pnt(0, 0, 0), 20, 20, 20)
box1_faces = list(TopologyExplorer(box1).faces())
box1_shell = TopoDS_Shell()
bild = BRep_Builder()
bild.MakeShell(box1_shell)
for shp in [box1_faces[0], box1_faces[2]]:
    bild.Add(box1_shell, shp)
display.DisplayShape(box1_shell, transparency=0.7)

box2 = make_box(gp_Pnt(40, 0, 0), 20, 20, 20)
box2_trsf = gp_Trsf()
box2_trsf.SetRotation(gp_Ax1(gp_Pnt(40, 0, 0), gp_Dir(0, 0, 1)), np.deg2rad(0))
box2_faces = list(TopologyExplorer(box2).faces())
box2_shell = TopoDS_Shell()
bild = BRep_Builder()
bild.MakeShell(box2_shell)
for shp in [box2_faces[0], box2_faces[2]]:
    bild.Add(box2_shell, shp)
display.DisplayShape(box2_shell, transparency=0.7)

display.FitAll()
start_display()
