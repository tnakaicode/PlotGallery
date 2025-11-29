"""
Create a B-spline surface from a grid of 3D points, trim it using a polygon
in UV parameter space (FaceRestrictor), extract the resulting wire(s), and
sample points along the wire(s) using GCPnts_UniformAbscissa.

This file demonstrates:
- GeomAPI_PointsToBSplineSurface
- Mapping a 2D UV polygon to a wire on the surface
- BRepAlgo_FaceRestrictor to trim the surface
- Sampling edges on the resulting wire(s) using GCPnts_UniformAbscissa
- Displaying the surface, wire and sampled points using OCC viewer

Run as script: it will open the OCC viewer and show results.
"""

from __future__ import annotations

import math
import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Pnt2d, gp_Dir, gp_Ax2
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomAbs import GeomAbs_G2
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCC.Core.BRepProj import BRepProj_Projection
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeVertex,
)
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_EDGE
from OCC.Core.TopoDS import topods
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_UniformAbscissa
from OCC.Core.gp import gp_Circ
from OCCUtils.Construct import make_polygon, make_wire, make_face
from OCC.Display.SimpleGui import init_display


def make_bspline_surface(nx=10, ny=10):
    """Build a bspline surface from a grid of points with gentle z-variation."""
    arr = TColgp_Array2OfPnt(1, nx, 1, ny)
    for i in range(1, nx + 1):
        for j in range(1, ny + 1):
            x = (i - 1) / nx
            y = (j - 1) / ny
            z = 0.1 * math.sin(x * 3) * math.cos(y * 5)
            arr.SetValue(i, j, gp_Pnt(x, y, z))

    api = GeomAPI_PointsToBSplineSurface(arr, 3, 3, GeomAbs_G2, 1e-6)
    # Interpolate and get surface
    api.Interpolate(arr)
    surf = api.Surface()
    return surf


def polygon2d_to_wire_on_surface(surface, uv_points):
    """Map a polygon given in UV param space to a wire lying on the surface.

    The uv_points are in the parameter domain of the surface (commonly 0..1).
    We create 2D segments in param space and lift them to edges on the surface.
    """
    edges = []
    n = len(uv_points)
    for i in range(n):
        u1, v1 = uv_points[i]
        u2, v2 = uv_points[(i + 1) % n]
        seg2d = GCE2d_MakeSegment(gp_Pnt2d(u1, v1), gp_Pnt2d(u2, v2)).Value()
        e = BRepBuilderAPI_MakeEdge(seg2d, surface).Edge()
        edges.append(e)

    wb = BRepBuilderAPI_MakeWire()
    for e in edges:
        wb.Add(e)
    return wb.Wire()


def make_planar_polygon_wire(points2d, z=0.0):
    """Make a 3D wire lying on the plane z=z from a list of 2D points."""
    edges = []
    n = len(points2d)
    for i in range(n):
        x1, y1 = points2d[i]
        x2, y2 = points2d[(i + 1) % n]
        e = BRepBuilderAPI_MakeEdge(gp_Pnt(x1, y1, z), gp_Pnt(x2, y2, z)).Edge()
        edges.append(e)
    wb = BRepBuilderAPI_MakeWire()
    for e in edges:
        wb.Add(e)
    return wb.Wire()


def project_wire_to_surface(planar_wire, surface, dir_vec=None):
    """Project a planar wire onto `surface` along `dir_vec` (gp_Dir).

    Returns the projected wire if available, otherwise None.
    """
    if dir_vec is None:
        dir_vec = gp_Dir(0, 0, 1)
    proj = BRepProj_Projection(planar_wire, surface, dir_vec)
    # iterate through projection results and return the last/current
    result = proj.Current()
    return result


def sample_edge_uniform(edge, n_points: int = 11):
    """Sample an OCC Edge uniformly using GCPnts_UniformAbscissa with fallback."""
    if n_points < 2:
        raise ValueError("n_points must be >= 2")

    adaptor = BRepAdaptor_Curve(edge)
    ua = GCPnts_UniformAbscissa(adaptor, n_points)
    pts = []
    if ua is not None and ua.IsDone() and ua.NbPoints() >= 2:
        for i in range(1, ua.NbPoints() + 1):
            u = ua.Parameter(i)
            p = adaptor.Value(u)
            pts.append((p.X(), p.Y(), p.Z()))
        return pts

    # fallback to uniform parameter sampling
    first = adaptor.FirstParameter()
    last = adaptor.LastParameter()
    for u in np.linspace(first, last, n_points):
        p = adaptor.Value(float(u))
        pts.append((p.X(), p.Y(), p.Z()))
    return pts


def sample_wires_on_face(face, n_points_per_edge=12):
    """Extract wires from a face and sample each edge on them.

    Returns a list of (wire, pts_on_wire) pairs where pts_on_wire is concatenated
    sample points along the wire.
    """
    wires = []
    exp = TopExp_Explorer(face, TopAbs_WIRE)
    while exp.More():
        w = topods.Wire(exp.Current())
        # iterate edges in wire
        pts_wire = []
        edge_exp = TopExp_Explorer(w, TopAbs_EDGE)
        first_added = False
        while edge_exp.More():
            e = topods.Edge(edge_exp.Current())
            pts_edge = sample_edge_uniform(e, n_points_per_edge)
            if pts_edge:
                if pts_wire and np.allclose(pts_wire[-1], pts_edge[0]):
                    pts_wire.extend(pts_edge[1:])
                else:
                    pts_wire.extend(pts_edge)
            edge_exp.Next()
        wires.append((w, pts_wire))
        exp.Next()
    return wires


if __name__ == "__main__":
    display, start_display, _, _ = init_display()

    # build bspline surface
    surf = make_bspline_surface(nx=10, ny=10)

    # make a face from full surface
    base_face = BRepBuilderAPI_MakeFace(surf, 1e-6).Face()

    # define a polygon in planar XY (unit coordinates) and create planar wire
    # We'll create the polygon in a plane and project it onto the surface.
    planar_poly = [
        gp_Pnt(0.15, 0.15, 0),
        gp_Pnt(0.85, 0.15, 0),
        gp_Pnt(0.85, 0.6, 0),
        gp_Pnt(0.55, 0.8, 0),
        gp_Pnt(0.25, 0.7, 0),
    ]
    planar_wire = make_polygon(planar_poly, closed=True)
    # project planar wire onto the BSpline surface (along +Z)
    # BRepProj_Projection expects TopoDS shapes; pass the created base_face
    wire_on_surf = project_wire_to_surface(planar_wire, base_face, gp_Dir(0, 0, 1))
    wire_cir1 = make_wire(
        BRepBuilderAPI_MakeEdge(
            gp_Circ(gp_Ax2(gp_Pnt(0.5, 0.5, 0), gp_Dir(0, 0, 1)), 0.1)
        ).Edge()
    )
    wire_cir1_on_surf = project_wire_to_surface(wire_cir1, base_face, gp_Dir(0, 0, 1))

    holed_face = BRepBuilderAPI_MakeFace(base_face, wire_cir1_on_surf).Face()

    # try face restrictor to trim
    fr = BRepAlgo_FaceRestrictor()
    fr.Init(holed_face, False, True)
    fr.Add(wire_on_surf)
    fr.Perform()

    if fr.IsDone() and fr.More():
        result_face = fr.Current()

    # display
    display.DisplayShape(base_face, color="BLUE1", transparency=0.6)
    display.DisplayShape(planar_wire, color="RED", update=True)
    display.DisplayShape(wire_on_surf, color="RED")
    display.DisplayShape(holed_face, color="YELLOW", transparency=0.5)
    # display.DisplayShape(result_face, color="GREEN", transparency=0.5)

    # sample wires
    target_per_edge = 16
    wires_pts = [(wire_on_surf, [])]
    exp = TopExp_Explorer(holed_face, TopAbs_EDGE)
    while exp.More():
        e = topods.Edge(exp.Current())
        wires_pts[0][1].extend(sample_edge_uniform(e, target_per_edge))
        exp.Next()

    # show sampled points
    for w, pts in wires_pts:
        for p in pts:
            display.DisplayShape(gp_Pnt(*p))

    display.FitAll()
    start_display()
