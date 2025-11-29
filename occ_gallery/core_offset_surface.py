"""
Demo: create a BSpline surface and its offset using OpenCASCADE, then display both faces.
This script tries to be robust across typical PythonOCC installs.
"""

import sys
import math

from OCC.Display.SimpleGui import init_display
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.Geom import Geom_OffsetSurface
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_SHELL, TopAbs_EDGE
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet, BRepFilletAPI_MakeChamfer
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid


def make_bspline_surface(nx=6, ny=6):
    # create a simple wavy surface over [0,1]x[0,1]
    t = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(1, nx + 1):
        u = (i - 1) / (nx - 1)
        for j in range(1, ny + 1):
            v = (j - 1) / (ny - 1)
            z = 0.15 * math.sin(math.pi * u * 1.5) * math.sin(math.pi * v * 1)
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


def build_solid_from_faces(face0, face1, tol=1e-6):
    """Given two TopoDS_Face objects (original and offset), build a connecting
    loft shell, sew faces and shell, and return (solid, loft_shell).
    Returns (None, None) if construction cannot be completed.
    """
    exp0 = TopExp_Explorer(face0, TopAbs_WIRE)
    wires0 = []
    while exp0.More():
        wires0.append(exp0.Current())
        exp0.Next()

    exp1 = TopExp_Explorer(face1, TopAbs_WIRE)
    wires1 = []
    while exp1.More():
        wires1.append(exp1.Current())
        exp1.Next()

    if not wires0 or not wires1:
        return None, None

    w0 = wires0[0]
    w1 = wires1[0]

    thru = BRepOffsetAPI_ThruSections(True, True, tol)
    thru.AddWire(w0)
    thru.AddWire(w1)
    thru.Build()
    loft_shell = thru.Shape()

    sewing = BRepBuilderAPI_Sewing(tol)
    sewing.Add(face0)
    sewing.Add(face1)
    sewing.Add(loft_shell)
    sewing.Perform()
    sewed = sewing.SewedShape()

    exp_shell = TopExp_Explorer(sewed, TopAbs_SHELL)
    shell_found = None
    while exp_shell.More():
        shell_found = exp_shell.Current()
        break

    shell_to_use = shell_found if shell_found is not None else sewed

    maker = BRepBuilderAPI_MakeSolid()
    maker.Add(shell_to_use)
    solid = maker.Solid()

    return solid, loft_shell


def apply_fillet(solid, radius=0.02):
    """Apply a fillet of given radius to all edges of the solid and return the filleted solid."""
    fillet = BRepFilletAPI_MakeFillet(solid)
    exp_e = TopExp_Explorer(solid, TopAbs_EDGE)
    edges = []
    while exp_e.More():
        edges.append(exp_e.Current())
        exp_e.Next()

    for e in edges:
        fillet.Add(radius, e)

    fillet.Build()
    return fillet.Shape()


def get_edges_from_face(face):
    """Return a list of TopoDS_Edge objects belonging to the given face."""
    exp = TopExp_Explorer(face, TopAbs_EDGE)
    edges = []
    while exp.More():
        edges.append(exp.Current())
        exp.Next()
    return edges


def apply_chamfer(solid, edges, distance=0.02):
    """Apply chamfer of given distance to provided edges on the solid and return the modified shape."""
    chamfer = BRepFilletAPI_MakeChamfer(solid)
    for e in edges:
        chamfer.Add(distance, e)
    chamfer.Build()
    return chamfer.Shape()


def apply_fillet(solid, edges, distance=0.02):
    """Apply fillet of given distance to provided edges on the solid and return the modified shape."""
    fillet = BRepFilletAPI_MakeFillet(solid)
    for e in edges:
        fillet.Add(distance, e)
    fillet.Build()
    return fillet.Shape()


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    surf = make_bspline_surface(6, 6)

    # create an offset surface (positive offset along surface normal)
    offset_val = 0.12
    off_surf = Geom_OffsetSurface(surf, offset_val)

    # make faces
    face0 = make_face_from_surface(surf)
    face1 = make_face_from_surface(off_surf)

    solid, loft_shell = build_solid_from_faces(face0, face1)

    # display original surface (blue), offset surface (green), loft (yellow) and solid (red)
    # display.DisplayShape(face0, update=True, transparency=0.5, color="BLUE1")
    # display.DisplayShape(face1, update=True, transparency=0.5, color="GREEN")
    # if loft_shell is not None:
    #    display.DisplayShape(loft_shell, update=True, transparency=0.6, color="YELLOW")

    filleted = None
    if solid is not None:
        # apply chamfer to bottom face edges (face0), then fillet to top face edges (face1)
        bottom_edges = get_edges_from_face(face0)
        top_edges = get_edges_from_face(face1)

        # chamfer bottom edges first
        solid_chamfered = apply_chamfer(solid, bottom_edges, distance=0.02)

        # then fillet top edges on the chamfered solid
        # note: we use the original top_edges collected from face1
        solid_filleted = apply_fillet(solid_chamfered, top_edges, distance=0.02)

        # display original solid (red, transparent), chamfered+filleted result (magenta)
        # display.DisplayShape(solid, update=True, transparency=0.6, color="RED")
        display.DisplayShape(solid_filleted, update=True, transparency=0.5)

    display.FitAll()
    start_display()
