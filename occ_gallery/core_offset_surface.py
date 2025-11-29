"""
Demo: create a BSpline surface and its offset using OpenCASCADE, then display both faces.
This script tries to be robust across typical PythonOCC installs.
"""

import sys
import math

from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.Geom import Geom_OffsetSurface
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Display.SimpleGui import init_display


def make_bspline_surface(nx=6, ny=6):
    # create a simple wavy surface over [0,1]x[0,1]
    t = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(1, nx + 1):
        u = (i - 1) / (nx - 1)
        for j in range(1, ny + 1):
            v = (j - 1) / (ny - 1)
            z = 0.15 * math.sin(math.pi * u) * math.sin(math.pi * v)
            t.SetValue(i, j, gp_Pnt(u, v, z))
    builder = GeomAPI_PointsToBSplineSurface(t)
    surf = builder.Surface()
    return surf


def make_face_from_surface(surf):
    # Try to make a face from the surface. Use a few fallbacks if overloads differ.

    mk = BRepBuilderAPI_MakeFace(surf, 1e-6)
    if mk.IsDone():
        return mk.Face()

    # Try alternate overload without tolerance
    mk = BRepBuilderAPI_MakeFace(surf)
    if mk.IsDone():
        return mk.Face()

    # As a last resort return None
    return None


if __name__ == "__main__":
    surf = make_bspline_surface(6, 6)

    # create an offset surface (positive offset along surface normal)
    offset_val = 0.12
    off_surf = Geom_OffsetSurface(surf, offset_val)

    # make faces
    face0 = make_face_from_surface(surf)
    face1 = make_face_from_surface(off_surf)

    if face0 is None or face1 is None:
        print("Failed to build faces from surfaces. Faces are required for display.")
        sys.exit(1)

    display, start_display, add_menu, add_function_to_menu = init_display()

    # display original surface (blue) and offset surface (green)
    display.DisplayShape(face0, update=True, transparency=0.5, color="BLUE1")
    display.DisplayShape(face1, update=True, transparency=0.5, color="GREEN")

    display.FitAll()
    start_display()
