# Copyright 2009-2018 Thomas Paviot (tpaviot@gmail.com)
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
import sys
import random
from math import pi

from OCC.Core.BRep import BRep_Tool_Surface
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Section, BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_GTransform,
)
from OCC.Core.BRepFeat import (
    BRepFeat_MakePrism,
    BRepFeat_MakeDPrism,
    BRepFeat_SplitShape,
    BRepFeat_MakeLinearForm,
    BRepFeat_MakeRevol,
)
from OCC.Core.BRepLib import breplib_BuildCurves3d
from OCC.Core.BRepOffset import BRepOffset_Skin
from OCC.Core.BRepOffsetAPI import (
    BRepOffsetAPI_MakeThickSolid,
    BRepOffsetAPI_MakeOffsetShape,
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakePrism
from OCC.Display.SimpleGui import init_display
from OCC.Core.GCE2d import GCE2d_MakeLine
from OCC.Core.Geom import Geom_Plane
from OCC.Core.Geom2d import Geom2d_Circle
from OCC.Core.GeomAbs import GeomAbs_Arc
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.gp import (
    gp_Pnt2d,
    gp_Circ2d,
    gp_Ax2d,
    gp_Dir2d,
    gp_Pnt,
    gp_Pln,
    gp_Vec,
    gp_OX,
    gp_Trsf,
    gp_GTrsf,
)

from OCC.Extend.TopologyUtils import TopologyExplorer

display, start_display, add_menu, add_function_to_menu = init_display()


def face_from_vert(event=None):
    # https://docs.python.org/ja/3/library/secrets.html
    pts = []
    dat = np.random.rand(3, 10)
    for xyz in dat:
        pts.append(gp_Pnt(*xyz))

    S = BRepPrimAPI_MakeBox(150, 200, 110).Shape()

    topo = TopologyExplorer(S)
    vert = next(topo.vertices())

    shapes = TopTools_ListOfShape()
    for f in topo.faces_from_vertex(vert):
        shapes.Append(f)

    ts = BRepOffsetAPI_MakeThickSolid()
    ts.MakeThickSolidByJoin(S, shapes, 15, 0.01)
    ts.Build()
    _thick_solid = ts.Shape()

    display.EraseAll()
    display.DisplayShape(_thick_solid)
    display.FitAll()


def thick_solid(event=None):
    S = BRepPrimAPI_MakeBox(150, 200, 110).Shape()

    topo = TopologyExplorer(S)
    vert = next(topo.vertices())

    shapes = TopTools_ListOfShape()
    for f in topo.faces_from_vertex(vert):
        shapes.Append(f)

    ts = BRepOffsetAPI_MakeThickSolid()
    ts.MakeThickSolidByJoin(S, shapes, 15, 0.01)
    ts.Build()
    _thick_solid = ts.Shape()

    display.EraseAll()
    display.DisplayShape(_thick_solid)
    display.FitAll()


def exit(event=None):
    sys.exit()


if __name__ == "__main__":
    add_menu("topology local operations")
    add_function_to_menu("topology local operations", thick_solid)
    add_function_to_menu("topology local operations", exit)
    start_display()
