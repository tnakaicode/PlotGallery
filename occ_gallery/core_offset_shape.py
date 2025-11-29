# Example: create a BSpline surface, trim by polygon and offset using BRepOffsetAPI_MakeOffsetShape
# Uses absolute imports and displays results in the OCC viewer

from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_Vec, gp_Dir
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomAbs import GeomAbs_G2
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace,
)
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCC.Core.BRepOffset import BRepOffset_Skin
from OCC.Core.GeomAbs import GeomAbs_Arc
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Display.SimpleGui import init_display
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRepLib import breplib

import math


def make_bspline_surface(nx=10, ny=10):
    """Build a bspline surface from a grid of points (portable GeomAPI usage)."""
    arr = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            x = (i - 1) / (nx - 1)
            y = (j - 1) / (ny - 1)
            z = 0.05 * math.sin(x * 3.0) * math.cos(y * 5.0)
            arr.SetValue(i, j, gp_Pnt(x * 200.0, y * 200.0, z * 40.0))

    api = GeomAPI_PointsToBSplineSurface(arr, 3, 3, GeomAbs_G2, 1e-6)
    try:
        api.Interpolate(arr)
    except Exception:
        # some pythonocc versions already build the surface on construction
        pass
    surf = api.Surface()
    return surf


def make_polygon_wire(origin=(20, 30), pts=None):
    if pts is None:
        # default rectangle polygon (in surface param-space units)
        x0, y0 = origin
        pts = [
            (x0 + 20, y0 + 20),
            (x0 + 160, y0 + 20),
            (x0 + 160, y0 + 140),
            (x0 + 20, y0 + 140),
        ]
    wire_maker = BRepBuilderAPI_MakeWire()
    # Make 3D edges using the surface's parametric 2D points projected later when needed.
    # Here we create edges as straight segments in 3D (z=0) then use them with Init(face, ...) to add
    # as 2D edges on the surface.
    for i in range(len(pts)):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % len(pts)]
        e = BRepBuilderAPI_MakeEdge(gp_Pnt(x1, y1, 0.0), gp_Pnt(x2, y2, 0.0)).Edge()
        wire_maker.Add(e)
    wire_maker.Build()
    return wire_maker.Wire()


def trim_surface_with_polygon(surf, polygon_pts=None):
    # Make a face from the surface (untrimmed)
    mkface = BRepBuilderAPI_MakeFace()
    # MkFace.Init(surf, ...) overloads: use Init(Geom_Surface, param) if available
    try:
        mkface.Init(surf, False, 1e-6)
    except Exception:
        # try simpler MakeFace(surf)
        mkface = BRepBuilderAPI_MakeFace(surf, 1e-6)
    # Create polygon wire in 3D lying near z=0; we rely on breplib.BuildCurves3d to project
    wire = make_polygon_wire(pts=polygon_pts)
    mkface.Add(wire)
    mkface.Build()
    face = mkface.Face()
    # Rebuild 3D curves on the face to make PCurves consistent
    try:
        breplib.BuildCurves3d(face)
    except Exception:
        pass
    return face


def offset_face_using_makeoffsetshape(shape, offset=-10.0, tol=1e-3):
    # shape can be a TopoDS_Shape (e.g., Face or Shell); use MakeOffsetShape.PerformByJoin
    offset_api = BRepOffsetAPI_MakeOffsetShape()
    # PerformByJoin(shape, offset, tol, skin, remove, join, mode)
    # Using BRepOffset_Skin and GeomAbs_Arc mode similar to examples
    offset_api.PerformByJoin(
        shape, offset, tol, BRepOffset_Skin, False, False, GeomAbs_Arc
    )
    return offset_api


if __name__ == "__main__":
    surf = make_bspline_surface()
    face = trim_surface_with_polygon(surf)

    # Initialize viewer and display results
    display, start_display, add_menu, add_function_to_menu = init_display()

    display.DisplayShape(face)

    offset_api = offset_face_using_makeoffsetshape(face, offset=-20.0)
    off_shape = offset_api.Shape()
    display.DisplayShape(off_shape)

    display.FitAll()
    start_display()
