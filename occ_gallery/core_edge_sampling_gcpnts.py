"""
Examples: sample edges/wires uniformly using GCPnts_UniformAbscissa

This script demonstrates using OCC's GCPnts_UniformAbscissa (with
BRepAdaptor_Curve) to sample various Edge types:
- straight line edge
- circular arc (full circle and partial arc)
- ellipse arc
- BSpline curve constructed from points
- sampling a Wire composed of multiple edges

Functions:
- sample_edge_uniform(edge, n_points): returns list of (x,y,z) points
- sample_wire_uniform(wire, n_points_per_edge): concatenates per-edge samples

Run as a script to print sampled points and show a simple matplotlib plot.
"""

from __future__ import annotations

import math
import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Dir
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeVertex,
)
from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.GCPnts import GCPnts_UniformAbscissa
from OCC.Core.TopoDS import topods
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE

# For constructing analytic curves
from OCC.Core.Geom import Geom_Circle, Geom_Ellipse
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt


def sample_edge_uniform(edge, n_points: int = 11):
    """Sample an OCC Edge uniformly (parametric) using GCPnts_UniformAbscissa.

    Parameters:
    - edge: TopoDS_Edge
    - n_points: target number of sample points along the curve (>=2)

    Returns:
    - list of (x,y,z) tuples of sampled points

    Notes:
    - GCPnts_UniformAbscissa tries to place points at equal arc-length spacing.
    - If it fails, this function falls back to uniform param sampling.
    """
    if n_points < 2:
        raise ValueError("n_points must be >= 2")

    adaptor = BRepAdaptor_Curve(edge)

    ua = GCPnts_UniformAbscissa(adaptor, n_points)

    pts = []

    if ua is not None and ua.IsDone() and ua.NbPoints() >= 2:
        # GCPnts returns param values accessible by Parameter(i) for i=1..NbPoints()
        for i in range(1, ua.NbPoints() + 1):
            u = ua.Parameter(i)
            p = adaptor.Value(u)
            pts.append((p.X(), p.Y(), p.Z()))
        return pts

    # Fallback: uniform parameter sampling
    first = adaptor.FirstParameter()
    last = adaptor.LastParameter()
    for u in np.linspace(first, last, n_points):
        p = adaptor.Value(float(u))
        pts.append((p.X(), p.Y(), p.Z()))
    return pts


def sample_wire_uniform(wire, n_points_per_edge: int = 11):
    """Sample all edges in a wire and return concatenated point lists.

    Parameters:
    - wire: TopoDS_Wire
    - n_points_per_edge: target points per edge
    """
    out_pts = []
    exp = TopExp_Explorer(wire, TopAbs_EDGE)
    while exp.More():
        e = topods.Edge(exp.Current())
        pts = sample_edge_uniform(e, n_points_per_edge)
        # avoid duplicating the first point if it matches the last added
        if out_pts and np.allclose(out_pts[-1], pts[0]):
            out_pts.extend(pts[1:])
        else:
            out_pts.extend(pts)
        exp.Next()
    return out_pts


# helpers to build example edges


def make_line_edge(x0=0, y0=0, z0=0, x1=1, y1=0, z1=0):
    return BRepBuilderAPI_MakeEdge(gp_Pnt(x0, y0, z0), gp_Pnt(x1, y1, z1)).Edge()


def make_circle_edge(center=(0, 0, 0), radius=1.0, start_ang=0.0, end_ang=2 * math.pi):
    ax = gp_Ax2(gp_Pnt(*center), gp_Dir(0, 0, 1))
    circle = Geom_Circle(ax, float(radius))
    # create an edge from the analytic circle; BRepBuilderAPI_MakeEdge accepts (Geom_Curve, first, last)
    return BRepBuilderAPI_MakeEdge(circle, float(start_ang), float(end_ang)).Edge()


def make_ellipse_edge(
    center=(0, 0, 0), major=2.0, minor=1.0, start_ang=0.0, end_ang=2 * math.pi
):
    ax = gp_Ax2(gp_Pnt(*center), gp_Dir(0, 0, 1))
    ellipse = Geom_Ellipse(ax, float(major), float(minor))
    return BRepBuilderAPI_MakeEdge(ellipse, float(start_ang), float(end_ang)).Edge()


def make_bspline_edge(points):
    """Create a BSpline curve through given control/sample points and return an edge."""
    # points: iterable of (x,y,z)
    gp_pts = [gp_Pnt(*p) for p in points]
    n = len(gp_pts)
    if n < 2:
        raise ValueError("Need at least 2 points to build a BSpline")
    arr = TColgp_Array1OfPnt(1, n)
    for i, p in enumerate(gp_pts, start=1):
        arr.SetValue(i, p)
    builder = GeomAPI_PointsToBSpline(arr)
    bspline = builder.Curve()
    return BRepBuilderAPI_MakeEdge(bspline).Edge()


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    # examples and quick prints
    examples = []

    # 1) straight line
    e_line = make_line_edge(0, 0, 0, 0.1, 0, 0)
    p_line = sample_edge_uniform(e_line, n_points=5)
    print("Line edge: points=", len(p_line))

    # 2) full circle (closed)
    e_circle = make_circle_edge(
        center=(0.2, 0.2, 0), radius=0.05, start_ang=0.0, end_ang=2 * math.pi
    )
    p_circle = sample_edge_uniform(e_circle, n_points=21)
    print("Circle edge: points=", len(p_circle))

    # 3) circular arc (half)
    e_arc = make_circle_edge(
        center=(0.5, 0.2, 0), radius=0.04, start_ang=0.0, end_ang=math.pi
    )
    p_arc = sample_edge_uniform(e_arc, n_points=11)
    print("Arc edge (half-circle): points=", len(p_arc))

    # 4) ellipse
    e_ell = make_ellipse_edge(
        center=(0.9, 0.2, 0), major=0.07, minor=0.03, start_ang=0.0, end_ang=2 * math.pi
    )
    p_ell = sample_edge_uniform(e_ell, n_points=31)
    print("Ellipse edge: points=", len(p_ell))

    # 5) BSpline through points
    ctrl = [(0.0, 0.6, 0), (0.02, 0.63, 0), (0.04, 0.58, 0), (0.06, 0.62, 0)]
    e_bs = make_bspline_edge(ctrl)
    p_bs = sample_edge_uniform(e_bs, n_points=15)
    print("BSpline edge: points=", len(p_bs))

    # 6) wire composed of several edges
    try:
        mk = BRepBuilderAPI_MakeWire()
        mk.Add(e_line)
        mk.Add(e_arc)
        mk.Add(e_bs)
        wire = mk.Wire()
        p_wire = sample_wire_uniform(wire, n_points_per_edge=8)
        print("Wire: total sample points=", len(p_wire))
    except Exception:
        # fallback: concatenate per-edge samples
        p_wire = []
        for e in (e_line, e_arc, e_bs):
            pts = sample_edge_uniform(e, 8)
            if p_wire and np.allclose(p_wire[-1], pts[0]):
                p_wire.extend(pts[1:])
            else:
                p_wire.extend(pts)
        print("Wire (fallback, concatenated edges): total sample points=", len(p_wire))

    # show analytic edges
    display.DisplayShape(e_line, update=False)
    display.DisplayShape(e_circle, update=False)
    display.DisplayShape(e_arc, update=False)
    display.DisplayShape(e_ell, update=False)
    display.DisplayShape(e_bs, update=False)

    # show sampled points as small vertices (may be more visible depending on viewer settings)
    for pts in (p_line, p_circle, p_arc, p_ell, p_bs, p_wire):
        for p in pts:
            try:
                v = BRepBuilderAPI_MakeVertex(gp_Pnt(*p)).Vertex()
                display.DisplayShape(v, update=False)
            except Exception:
                # skip points that cannot be shown
                continue
    display.FitAll()
    start_display()
