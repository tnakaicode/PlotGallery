# Example: create a BSpline surface, trim by polygon and offset using BRepOffsetAPI_MakeOffsetShape
# Uses absolute imports and displays results in the OCC viewer

from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_Vec, gp_Dir
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomAbs import GeomAbs_G2
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCC.Core.Geom import Geom_OffsetSurface
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
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeSolid
from OCC.Core.TopAbs import TopAbs_SHELL
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopoDS import topods
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakeOffsetShape
from OCC.Core.BRepOffset import BRepOffset_Skin
import math
import numpy as np
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_UniformAbscissa
from OCC.Core.TopoDS import topods


def make_bspline_surface(nx=20, ny=20):
    """Build a more strongly varying bspline surface from a grid of points.

    Increased frequency and amplitude so the surface has larger curvature
    and height variation for testing offset behavior.
    """
    arr = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            x = (i - 1) / (nx - 1)
            y = (j - 1) / (ny - 1)
            # stronger oscillation and amplitude
            z = 0.2 * math.sin(math.pi * x * 2.0) * math.cos(math.pi * y * 1.0)
            arr.SetValue(i, j, gp_Pnt(x * 200.0, y * 200.0, z * 80.0))

    api = GeomAPI_PointsToBSplineSurface(arr, 4, 4, GeomAbs_G2, 1e-6)
    api.Interpolate(arr)
    surf = api.Surface()
    return surf


def polygon_uv_to_wire_on_surface(surface, uv_pts):
    """Create a TopoDS_Wire on `surface` from a polygon given in UV param coordinates.

    `uv_pts` is a list of (u,v) pairs in the param domain of the surface (commonly 0..1).
    """
    wb = BRepBuilderAPI_MakeWire()
    n = len(uv_pts)
    for i in range(n):
        u1, v1 = uv_pts[i]
        u2, v2 = uv_pts[(i + 1) % n]
        seg2d = GCE2d_MakeSegment(gp_Pnt2d(u1, v1), gp_Pnt2d(u2, v2)).Value()
        e = BRepBuilderAPI_MakeEdge(seg2d, surface).Edge()
        wb.Add(e)
    wb.Build()
    return wb.Wire()


def trim_surface_with_polygon(surf, uv_polygon=None, tol=1e-6):
    """Make a trimmed TopoDS_Face from `surf` using a polygon in UV param space.

    Returns the trimmed `TopoDS_Face`.
    """
    # Create the base face from the surface
    mkf = BRepBuilderAPI_MakeFace(surf, tol)
    base_face = mkf.Face()

    if uv_polygon is None:
        # default polygon in UV param space (0..1)
        uv_polygon = [(0.15, 0.15), (0.85, 0.15), (0.85, 0.6), (0.55, 0.8), (0.25, 0.7)]

    wire_on_surf = polygon_uv_to_wire_on_surface(surf, uv_polygon)
    # Build face with hole (add wire as inner boundary)
    mkf2 = BRepBuilderAPI_MakeFace()
    mkf2.Init(surf, False, tol)
    mkf2.Add(wire_on_surf)
    mkf2.Build()
    face = mkf2.Face()
    breplib.BuildCurves3d(face)
    return face, wire_on_surf, uv_polygon


def sample_edge_points(edge, n=20):
    adaptor = BRepAdaptor_Curve(edge)
    ua = GCPnts_UniformAbscissa(adaptor, float(max(2, n)))
    pts = []
    if ua.IsDone() and ua.NbPoints() >= 2:
        for i in range(1, ua.NbPoints() + 1):
            u = ua.Parameter(i)
            p = adaptor.Value(u)
            pts.append((p.X(), p.Y(), p.Z()))
        return pts
    # fallback: two endpoints
    first = adaptor.FirstParameter()
    last = adaptor.LastParameter()
    p1 = adaptor.Value(first)
    p2 = adaptor.Value(last)
    return [(p1.X(), p1.Y(), p1.Z()), (p2.X(), p2.Y(), p2.Z())]


def wire_to_pointlist(wire, n_total=120):
    # collect dense points per edge then resample to n_total along chord length
    exp_e = TopExp_Explorer(wire, TopAbs_EDGE)
    pts = []
    while exp_e.More():
        e = topods.Edge(exp_e.Current())
        pts_e = sample_edge_points(e, n=max(8, int(n_total / 10)))
        if pts and np.allclose(pts[-1], pts_e[0]):
            pts.extend(pts_e[1:])
        else:
            pts.extend(pts_e)
        exp_e.Next()
    # compute cumulative distances
    pts_arr = np.array(pts)
    if pts_arr.shape[0] < 2:
        return pts
    segs = np.linalg.norm(np.diff(pts_arr, axis=0), axis=1)
    dist = np.concatenate(([0.0], np.cumsum(segs)))
    total = dist[-1]
    if total == 0 or len(pts_arr) < 2:
        return pts
    target_d = np.linspace(0.0, total, n_total)
    resampled = []
    for td in target_d:
        idx = np.searchsorted(dist, td)
        if idx == 0:
            resampled.append(tuple(pts_arr[0]))
        elif idx >= len(dist):
            resampled.append(tuple(pts_arr[-1]))
        else:
            t0 = dist[idx - 1]
            t1 = dist[idx]
            if t1 == t0:
                resampled.append(tuple(pts_arr[idx]))
            else:
                alpha = (td - t0) / (t1 - t0)
                p = pts_arr[idx - 1] * (1 - alpha) + pts_arr[idx] * alpha
                resampled.append(tuple(p))
    return resampled


def points_to_poly_wire(pts):
    # remove consecutive duplicate points (within tolerance)
    arr = np.array(pts, dtype=float)
    if arr.shape[0] < 2:
        raise ValueError("Not enough points to build poly wire")
    diffs = np.linalg.norm(np.diff(arr, axis=0), axis=1)
    keep = [0]
    tol = 1e-9
    for i, d in enumerate(diffs, start=1):
        if d > tol:
            keep.append(i)
    filtered = arr[keep]
    # ensure closed: do not duplicate last point equal to first
    if np.allclose(filtered[0], filtered[-1]):
        filtered = filtered[:-1]

    wb = BRepBuilderAPI_MakeWire()
    n = len(filtered)
    if n < 2:
        raise ValueError("Not enough distinct points for poly wire")
    for i in range(n):
        x1, y1, z1 = filtered[i]
        x2, y2, z2 = filtered[(i + 1) % n]
        # skip zero-length edges
        if np.allclose((x1, y1, z1), (x2, y2, z2)):
            continue
        e = BRepBuilderAPI_MakeEdge(gp_Pnt(x1, y1, z1), gp_Pnt(x2, y2, z2)).Edge()
        wb.Add(e)
    wb.Build()
    return wb.Wire()


def offset_face_using_makeoffsetshape(shape, offset=-10.0, tol=1e-3):
    # shape can be a TopoDS_Shape (e.g., Face or Shell); use MakeOffsetShape.PerformByJoin
    offset_api = BRepOffsetAPI_MakeOffsetShape()
    # PerformByJoin(shape, offset, tol, skin, remove, join, mode)
    # Using BRepOffset_Skin and GeomAbs_Arc mode similar to examples
    offset_api.PerformByJoin(
        shape, offset, tol, BRepOffset_Skin, False, False, GeomAbs_Arc
    )
    return offset_api


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


if __name__ == "__main__":
    # Initialize viewer and display results
    display, start_display, add_menu, add_function_to_menu = init_display()

    print("STEP: start building BSpline surface")
    surf = make_bspline_surface()
    display.DisplayShape(surf, transparency=0.5)
    print("STEP: BSpline surface built")

    print("STEP: trimming surface with polygon")
    face, wire0, uv_polygon = trim_surface_with_polygon(surf)
    print("STEP: trim finished. face and wire created")

    print("STEP: displaying original face")
    display.DisplayShape(face)

    # Try to offset the trimmed TopoDS_Face directly with BRepOffsetAPI_MakeOffsetShape
    # and obtain an offset geometry (prefer topology-preserving offset).

    # find outer wire of the trimmed face (for display)
    exp = TopExp_Explorer(face, TopAbs_WIRE)
    if not exp.More():
        raise RuntimeError("No wire found on face to offset")
    wire0 = topods.Wire(exp.Current())
    display.DisplayShape(wire0)

    print("STEP: attempting BRepOffsetAPI_MakeOffsetShape.PerformByJoin on the face")
    offset_distance = 20.0
    offset_api = BRepOffsetAPI_MakeOffsetShape()
    # Parameters: shape, offset, tol, skin, remove, join, mode
    offset_api.PerformByJoin(
        face, offset_distance, 1e-3, BRepOffset_Skin, False, False, GeomAbs_Arc
    )
    offset_api.Build()
    print("STEP: offset_api.IsDone() ->", offset_api.IsDone())
    off_shape = offset_api.Shape()
    display.DisplayShape(off_shape)

    solid, loft_shell = build_solid_from_faces(face, off_shape, tol=1e-3)
    display.DisplayShape(solid, update=True, transparency=0.3)

    display.FitAll()
    start_display()
