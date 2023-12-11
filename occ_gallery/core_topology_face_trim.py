# Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
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
import math

from OCC.Core.gp import (
    gp_Pnt,
    gp_Sphere,
    gp_Ax3,
    gp_Dir,
    gp_Circ,
    gp_Ax2,
    gp_Ax22d,
    gp_Pnt2d,
    gp_Dir2d,
    gp_Vec2d,
    gp_Circ2d
)
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomAbs import GeomAbs_C2
from OCC.Core.Geom2d import Geom2d_Line, Geom2d_Circle, Geom2d_Ellipse
from OCC.Core.BRepLib import breplib
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_PINK
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
from OCC.Extend.DataExchange import write_step_file
from OCCUtils.Construct import make_edge2d, make_face, make_wire

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


if __name__ == "__main__":
    nx, ny = 100, 200
    px = np.linspace(-1, 1, nx) * 100 + 50
    py = np.linspace(-1, 1, ny) * 100 - 50
    mesh = np.meshgrid(px, py)
    data = mesh[0]**2 / 1000 + mesh[1]**2 / 2000
    print(data.shape)

    pts = TColgp_Array2OfPnt(1, ny, 1, nx)
    for (ix, iy), _ in np.ndenumerate(data):
        pts.SetValue(ix + 1, iy + 1,
                     gp_Pnt(mesh[0][ix, iy], mesh[1][ix, iy], data[ix, iy]))

    surf = GeomAPI_PointsToBSplineSurface(pts, 3, 8).Surface()
    print(surf.FirstUKnotIndex(), surf.LastUKnotIndex())
    print(surf.FirstVKnotIndex(), surf.LastVKnotIndex())

    face = make_face(surf, 0.1e-6)
    display.DisplayShape(face)

    a_face = BRepAdaptor_Surface(face)
    print(a_face.FirstUParameter(), a_face.LastUParameter())
    print(a_face.FirstVParameter(), a_face.LastVParameter())

    axs = gp_Ax22d(gp_Pnt2d(0.5, 0.5), gp_Dir2d(1, 1))
    c2d = Geom2d_Circle(axs, 0.2)
    c2d = Geom2d_Ellipse(axs, 0.3, 0.1)
    c_edge = BRepBuilderAPI_MakeEdge(c2d, surf).Edge()
    c_wire = make_wire(c_edge)

    api = BRepAlgo_FaceRestrictor()
    api.Init(face, True, True)
    api.Add(c_wire)
    api.Perform()
    print(api.IsDone())
    while api.More():
        face = api.Current()
        display.DisplayColoredShape(api.Current())
        print(face)
        api.Next()
    # write_step_file(face, "./core_topology_face_trim.stp")

    display.FitAll()
    start_display()
