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
    fuse_box = BRepAlgoAPI_Fuse(box1, box2).Shape()
    fuse_box = BRepAlgoAPI_Fuse(fuse_box, box3).Shape()

    pts = [gp_Pnt(1, 2, 0),
           gp_Pnt(2, 2, 0),
           gp_Pnt(2, 4, 1.5)]
    face = make_face(make_polygon(pts, closed=True))
    # fuse_box = BRepAlgoAPI_Fuse(fuse_box, face).Shape()
    # sew = BRepBuilderAPI_Sewing()
    # sew.Add(fuse_box)
    # sew.Add(face)
    # sew.Perform()
    # fuse_box = sew.SewedShape()

    # Make Compound by two boxes
    bild = BRep_Builder()
    boxs_comp = TopoDS_Compound()
    bild.MakeCompound(boxs_comp)
    bild.Add(boxs_comp, fuse_box)
    bild.Add(boxs_comp, face)

    Sphere = BRepPrimAPI_MakeSphere(gp_Pnt(1.5, 0.8, 1.0), 0.5).Shape()
    # Cut = BRepAlgoAPI_Cut(fuse_box, Sphere).Shape()
    Cut = BRepAlgoAPI_Cut(boxs_comp, Sphere).Shape()

    display.DisplayShape(Cut)
    print(Cut)
    # write_step_file(Cut, "core_topology_solid.stp")

    lin = gp_Lin(gp_Pnt(1, 0, 0.8), gp_Dir(0.2, 0.6, -0.1))
    api = BRepIntCurveSurface_Inter()
    api.Init(Cut, lin, 1.0E-9)
    dat = []
    while api.More():
        display.DisplayShape(api.Pnt())
        p = api.Point()
        p.Dump()
        data = [p.W(), p.U(), p.V(), p.Pnt(), api.Face(), p.Transition()]
        dat.append(data)
        # print(point.Values(gp_Pnt(p.X()+0.1, p.Y(), p.Z())))
        api.Next()
    lin_edge = make_edge(lin, -3, 3)
    display.DisplayShape(lin_edge)

    print(dat[0])
    dat.sort(key=lambda e: e[0])
    print(dat[0])

    lin_curv = Geom_Line(lin)
    t1, t2 = dat[0][0], dat[1][0]
    pnt = lin_curv.Value((t1 + t2) / 2)
    print(point_in_solid(Cut, pnt))
    display.DisplayShape(pnt)

    t1, t2 = dat[2][0], dat[3][0]
    pnt = lin_curv.Value((t1 + t2) / 2)
    print(point_in_solid(Cut, pnt))
    display.DisplayShape(pnt)

    pts = [
        gp_Pnt(0.333333 - 0.1, -2 - 0.1, 1.13333 - 0.1),
        gp_Pnt(0.5, -1.5, 1.05 + 0.2),
        gp_Pnt(1, 0, 0.8 + 0.3),
        gp_Pnt(1.36417 - 0.1, 1.09251, 0.617915 + 0.1),
        gp_Pnt(1.5, 1.5, 0.55 - 0.1),
        gp_Pnt(1.83636, 2.50909 + 0.2, 0.381818 + 0.1),
    ]
    spl_data = TColgp_Array1OfPnt(1, len(pts))
    for i, p in enumerate(pts):
        spl_data.SetValue(i + 1, p)
    spl_curv = GeomAPI_PointsToBSpline(spl_data, 3, 8).Curve()
    int_curv = GeomAdaptor_Curve(spl_curv)

    api = BRepIntCurveSurface_Inter()
    api.Init(Cut, int_curv, 1.0E-9)
    dat = []
    while api.More():
        display.DisplayShape(api.Pnt())
        p = api.Point()
        p.Dump()
        data = [p.W(), p.U(), p.V(), p.Pnt(), api.Face(), p.Transition()]
        dat.append(data)
        # print(point.Values(gp_Pnt(p.X()+0.1, p.Y(), p.Z())))
        api.Next()
    display.DisplayShape(spl_curv)

    print(dat[0])
    dat.sort(key=lambda e: e[0])
    print(dat[0])

    display.FitAll()
    start_display()
