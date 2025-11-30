# Demo: generate a clothoid (Euler spiral) by numeric sampling and display in pythonOCC
# Uses absolute imports. No external deps other than numpy and pythonocc-core.

import math
import numpy as np

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_WIRE


def sample_clothoid(a, length, n=400, k0=0.0, theta0=0.0, x0=0.0, y0=0.0):
    """
    Sample a clothoid numerically using trapezoidal integration.
    k(s) = k0 + a*s
    theta(s) = theta0 + k0*s + 0.5*a*s^2
    Returns Nx2 numpy array of (x,y).
    """
    s = np.linspace(0.0, length, n)
    theta = theta0 + k0 * s + 0.5 * a * s**2
    ds = s[1] - s[0]
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    # cumulative trapezoid integration
    # x[0]=0, x[i] = sum_{j=0..i-1} 0.5*(cos_j+cos_{j+1})*ds
    cx = np.concatenate(([0.0], np.cumsum((cos_t[:-1] + cos_t[1:]) * 0.5 * ds)))
    cy = np.concatenate(([0.0], np.cumsum((sin_t[:-1] + sin_t[1:]) * 0.5 * ds)))
    cx = cx + x0
    cy = cy + y0
    pts = np.column_stack((cx, cy))
    return pts


def make_poly_wire_from_points(pts):
    """Create a TopoDS_Wire by connecting consecutive sampled points with straight edges."""
    mkw = BRepBuilderAPI_MakeWire()
    if len(pts) < 2:
        raise ValueError("Need at least 2 points")
    prev = gp_Pnt(float(pts[0, 0]), float(pts[0, 1]), 0.0)
    for i in range(1, len(pts)):
        p = gp_Pnt(float(pts[i, 0]), float(pts[i, 1]), 0.0)
        e = BRepBuilderAPI_MakeEdge(prev, p).Edge()
        mkw.Add(e)
        prev = p
    mkw.Build()
    return mkw.Wire()


def print_topology_counts(shape, name="shape"):
    from OCC.Core.TopExp import TopExp_Explorer
    from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_WIRE, TopAbs_EDGE, TopAbs_VERTEX
    def count(sub):
        exp = TopExp_Explorer(shape, sub)
        c = 0
        while exp.More():
            c += 1
            exp.Next()
        return c
    print(f"TOPOLOGY - {name}:")
    print(f"  Wires: {count(TopAbs_WIRE)}, Edges: {count(TopAbs_EDGE)}, Vertices: {count(TopAbs_VERTEX)}")


if __name__ == '__main__':
    # Parameters for a clothoid: curvature rate a, total length L
    a = 0.002  # curvature growth (1/m^2)
    L = 200.0  # length of curve in same units as output
    n = 600    # sample density

    print("Sampling clothoid: a=", a, "L=", L, "n=", n)
    pts = sample_clothoid(a, L, n=n, k0=0.0, theta0=0.0, x0=0.0, y0=0.0)
    print("Sampled points:", pts.shape)

    # Create wire
    wire = make_poly_wire_from_points(pts)

    # Display
    display, start_display, _, _ = init_display()
    display.DisplayShape(wire, update=True)
    print_topology_counts(wire, "clothoid_wire")

    # Optionally display a few sample points as vertices
    # (make small vertex shapes so you can see the sampling density)
    # We'll mark every 50th sample as a small visual point (via edges)
    for i in range(0, len(pts), max(1, len(pts)//20)):
        p = pts[i]
        # tiny edge to force a marker (or could use AIS_Point if available)
        p1 = gp_Pnt(p[0], p[1], 0.0)
        p2 = gp_Pnt(p[0] + 0.0001, p[1], 0.0)
        e = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
        display.DisplayShape(e, update=False, color="RED")

    display.FitAll()
    start_display()
