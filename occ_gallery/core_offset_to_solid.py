"""
Create a solid by offsetting a surface and connecting the original and offset boundaries.
- Build BSpline surface
- Make face and offset face
- Extract outer wires and loft (ThruSections) between them
- Sew faces and lofted shell, then make solid
- Display result
"""
import sys
import math

from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.Geom import Geom_OffsetSurface
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.gp import gp_Pnt, gp_Trsf, gp_Vec
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_FACE, TopAbs_SHELL
from OCC.Core.TopoDS import topods_Wire, topods_Face, topods_Shell
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCC.Display.SimpleGui import init_display


def make_bspline_surface(nx=6, ny=6):
    t = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(1, nx + 1):
        u = (i - 1) / (nx - 1)
        for j in range(1, ny + 1):
            v = (j - 1) / (ny - 1)
            z = 0.15 * math.sin(math.pi * u) * math.sin(math.pi * v)
            t.SetValue(i, j, gp_Pnt(u, v, z))
    builder = GeomAPI_PointsToBSplineSurface(t)
    return builder.Surface()


def make_face(surf):
    try:
        mk = BRepBuilderAPI_MakeFace(surf, 1e-6)
        if mk.IsDone():
            return mk.Face()
    except Exception:
        pass
    try:
        mk = BRepBuilderAPI_MakeFace(surf)
        if mk.IsDone():
            return mk.Face()
    except Exception:
        pass
    return None


def outer_wire_of_face(face):
    exp = TopExp_Explorer(face, TopAbs_WIRE)
    wires = []
    while exp.More():
        w = topods_Wire(exp.Current())
        wires.append(w)
        exp.Next()
    if not wires:
        return None
    # Heuristic: return the first wire (outer)
    return wires[0]


def build_solid_from_face_and_offset(face, off_face):
    w0 = outer_wire_of_face(face)
    w1 = outer_wire_of_face(off_face)
    if w0 is None or w1 is None:
        raise RuntimeError('Could not find wires on faces')

    # Build lofted shell through wires
    thru = BRepOffsetAPI_ThruSections(True, True, 1e-6)
    thru.AddWire(w0)
    thru.AddWire(w1)
    try:
        thru.Build()
    except Exception as e:
        print('ThruSections Build failed:', e)
        raise
    shell_shape = thru.Shape()

    # Sew faces and shell
    sewing = BRepBuilderAPI_Sewing(1e-6)
    sewing.Add(face)
    sewing.Add(off_face)
    sewing.Add(shell_shape)
    sewing.Perform()
    sewed = sewing.SewedShape()

    # Extract shell from sewed shape
    exp = TopExp_Explorer(sewed, TopAbs_SHELL)
    shell = None
    while exp.More():
        shell = topods_Shell(exp.Current())
        break

    if shell is None:
        # maybe sewed is already a shell
        shell = sewed

    # Try make solid
    ms = BRepBuilderAPI_MakeSolid()
    try:
        ms.Add(shell)
        sol = ms.Solid()
    except Exception as e:
        print('MakeSolid failed:', e)
        sol = None

    return sol, shell_shape


def main():
    surf = make_bspline_surface(8, 8)
    face = make_face(surf)
    off_surf = Geom_OffsetSurface(surf, 0.12)
    off_face = make_face(off_surf)
    if face is None or off_face is None:
        print('Failed make faces')
        sys.exit(1)

    solid, loft_shell = build_solid_from_face_and_offset(face, off_face)

    display, start_display, _, _ = init_display()
    display.DisplayShape(face, update=True, color='BLUE1', transparency=0.4)
    display.DisplayShape(off_face, update=True, color='GREEN', transparency=0.3)
    if loft_shell is not None:
        display.DisplayShape(loft_shell, update=True, color='YELLOW', transparency=0.6)
    if solid is not None:
        display.DisplayShape(solid, update=True, color='RED', transparency=0.0)

    display.FitAll()
    start_display()

if __name__ == '__main__':
    main()
