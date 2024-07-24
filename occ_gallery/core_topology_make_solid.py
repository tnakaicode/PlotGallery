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
import time

from OCC.Core.BRepAlgoAPI import (
    BRepAlgoAPI_Fuse,
    BRepAlgoAPI_Common,
    BRepAlgoAPI_Section,
    BRepAlgoAPI_Cut,
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform, BRepBuilderAPI_Sewing
from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeWedge,
    BRepPrimAPI_MakeSphere,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeCylinder,
    BRepPrimAPI_MakeCone,
)
from OCC.Display.SimpleGui import init_display
from OCC.Extend.DataExchange import write_step_file
from OCC.Core.gp import gp_Vec, gp_Ax2, gp_Pnt, gp_Dir, gp_Pln, gp_Trsf, gp_Lin
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TopoDS import topods, TopoDS_Compound, TopoDS_CompSolid
from OCC.Core.Geom import Geom_Line
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.GeomAdaptor import GeomAdaptor_Curve
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepTools import breptools
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepIntCurveSurface import BRepIntCurveSurface_Inter
from OCC.Core.IntCurveSurface import IntCurveSurface_IntersectionPoint, IntCurveSurface_TransitionOnCurve
from OCCUtils.Construct import make_edge, make_polygon, make_face
from OCCUtils.Common import midpoint, point_in_solid


def translate_topods_from_vector(brep_or_iterable, vec, copy=False):
    """
    translate a brep over a vector
    @param brep:    the Topo_DS to translate
    @param vec:     the vector defining the translation
    @param copy:    copies to brep if True
    """
    trns = gp_Trsf()
    trns.SetTranslation(vec)
    brep_trns = BRepBuilderAPI_Transform(brep_or_iterable, trns, copy)
    brep_trns.Build()
    return brep_trns.Shape()


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    box1 = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 2, 1, 1).Shape()
    box2 = BRepPrimAPI_MakeBox(gp_Pnt(0.5, 0.5, 0), 2, 1, 1).Shape()
    box3 = BRepPrimAPI_MakeBox(gp_Pnt(-0.5, -2.0, 0.5), 1, 1, 1).Shape()
    sphere = BRepPrimAPI_MakeSphere(100).Shape()
    cylidner = BRepPrimAPI_MakeCylinder(100, 50).Shape()
    cone = BRepPrimAPI_MakeCone(10, 100, 50).Shape()
    
    write_step_file(box1, "box1.stp")
    write_step_file(sphere, "sphere.stp")
    write_step_file(cylidner, "cylinder.stp")
    write_step_file(cone, "cone.stp")

    display.FitAll()
    start_display()
