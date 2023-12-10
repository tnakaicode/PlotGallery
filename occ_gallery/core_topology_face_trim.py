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
    gp_Pnt2d,
    gp_Dir2d,
    gp_Vec2d
)
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
)
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomAbs import GeomAbs_C2
from OCC.Core.Geom2d import Geom2d_Line
from OCC.Core.BRepLib import breplib
from OCC.Core.Quantity import Quantity_Color, Quantity_NOC_PINK
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


if __name__ == "__main__":
    nx, ny = 100, 200
    px = np.linspace(-1, 1, nx) * 100 + 50
    py = np.linspace(-1, 1, ny) * 100 - 50
    mesh = np.meshgrid(px, py)
    surf = mesh[0]**2 / 1000 + mesh[1]**2 / 2000
    print(surf.shape)
    
    pts = TColgp_Array2OfPnt(1, ny, 1, nx)
    for (ix, iy), _ in np.ndenumerate(surf):
        pts.SetValue(ix+1, iy+1, gp_Pnt(mesh[0][ix,iy], mesh[1][ix,iy], surf[ix,iy]))

    face = GeomAPI_PointsToBSplineSurface(pts, 3, 8).Surface()
    print(face.FirstUKnotIndex(), face.LastUKnotIndex())
    print(face.FirstVKnotIndex(), face.LastVKnotIndex())
    display.DisplayShape(face)

    #bFace = BRepAlgo_FaceRestrictor()
    #bFace.Init(aFace, True, True)
    #bFace.Add(Wire1)
    #bFace.Perform()
    #print(bFace.IsDone())
    #while bFace.More():
    #    print()
    #    display.DisplayColoredShape(bFace.Current())
    #    bFace.Next()
    
    display.FitAll()
    start_display()
