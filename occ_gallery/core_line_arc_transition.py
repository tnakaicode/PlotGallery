# Demo: connect a line and an arc using a clothoid (Euler spiral) transition.
# Approach:
# - Given a line endpoint and direction, and an arc center+radius+initial angles,
#   compute a clothoid that transitions curvature from 0 to 1/R while matching
#   tangent orientation at the arc start.
# - Place clothoid start at the line endpoint and rotate to match the line direction.
# - Move the arc's start angle so the arc start point coincides with the clothoid end
#   (this shifts the arc along the circle to make a positional connection).
# - Draw everything as poly-wires for robustness.

import math
import numpy as np
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire


def sample_clothoid(a, length, n=400, k0=0.0, theta0=0.0):
    s = np.linspace(0.0, length, n)
    theta = theta0 + k0 * s + 0.5 * a * s**2
    ds = s[1] - s[0]
    cos_t = np.cos(theta)
    sin_t = np.sin(theta)
    cx = np.concatenate(([0.0], np.cumsum((cos_t[:-1] + cos_t[1:]) * 0.5 * ds)))
    cy = np.concatenate(([0.0], np.cumsum((sin_t[:-1] + sin_t[1:]) * 0.5 * ds)))
    pts = np.column_stack((cx, cy))
    return pts


def make_poly_wire_from_points_3d(pts):
    # Deprecated simple constructor. Use the vertex-aware builder instead.
    return make_poly_wire_from_points_3d_with_shared(None, pts)


def make_poly_wire_from_points_3d_with_shared(shared_vertex, pts, shared_index=None):
    """
    Build a wire from 3D points but optionally reuse a provided TopoDS_Vertex
    at the given shared_index (int). This ensures two wires can share the same
    TopoDS_Vertex object for exact topological connection.
    """
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex

    mkw = BRepBuilderAPI_MakeWire()
    n = len(pts)
    if n < 2:
        raise ValueError("Need at least 2 points")

    # create vertices list, reusing shared_vertex when index matches
    verts = [None] * n
    for i in range(n):
        if shared_vertex is not None and shared_index is not None and i == shared_index:
            verts[i] = shared_vertex
        else:
            p = gp_Pnt(float(pts[i, 0]), float(pts[i, 1]), float(pts[i, 2]))
            verts[i] = BRepBuilderAPI_MakeVertex(p).Vertex()

    # create edges using vertex overload so vertices are topologically reused
    for i in range(1, n):
        e = BRepBuilderAPI_MakeEdge(verts[i - 1], verts[i]).Edge()
        mkw.Add(e)

    mkw.Build()
    return mkw.Wire()


def rotate_translate_pts2d(pts2d, origin, angle):
    """Rotate (by angle) and translate pts2d (Nx2) to 3D points with z=0 and origin (x,y)."""
    ca = math.cos(angle)
    sa = math.sin(angle)
    rot = np.dot(pts2d, np.array([[ca, -sa], [sa, ca]]).T)
    rot[:, 0] += origin[0]
    rot[:, 1] += origin[1]
    pts3d = np.zeros((rot.shape[0], 3), dtype=float)
    pts3d[:, 0:2] = rot
    return pts3d


def sample_circle(center, R, angle_start, angle_end, n=120):
    # sample points along circular arc from angle_start to angle_end (rad)
    thetas = np.linspace(angle_start, angle_end, n)
    x = center[0] + R * np.cos(thetas)
    y = center[1] + R * np.sin(thetas)
    pts = np.column_stack((x, y, np.zeros_like(x)))
    return pts


def connect_line_arc_with_clothoid(line_end, line_dir, arc_center, arc_R, arc_start_angle, arc_end_angle):
    # compute arc tangent direction at start angle
    ta = np.array([-math.sin(arc_start_angle), math.cos(arc_start_angle)])  # tangent for CCW orientation
    # compute signed angle from line_dir to arc tangent
    def signed_angle(v_from, v_to):
        a = math.atan2(v_from[0]*v_to[1] - v_from[1]*v_to[0], v_from[0]*v_to[0] + v_from[1]*v_to[1])
        return a

    v0 = np.array([line_dir[0], line_dir[1]])
    v0 = v0 / np.linalg.norm(v0)
    delta_theta = signed_angle(v0, ta)
    # curvature of arc: signed depending on orientation (assume CCW positive)
    k1 = 1.0 / arc_R
    # ensure sign of k1 matches delta_theta
    if delta_theta < 0:
        k1 = -k1

    if abs(k1) < 1e-12:
        raise ValueError("Arc radius too large or zero curvature")

    # compute required clothoid length L from delta_theta = 0.5 * k1 * L
    L = 2.0 * delta_theta / k1
    if L <= 0:
        # if L <= 0, flip orientation (try alternative sign)
        L = abs(L)

    a = k1 / L  # curvature rate

    # sample clothoid in local frame
    pts2d = sample_clothoid(a, L, n=600, k0=0.0, theta0=0.0)
    # rotate+translate to place start at line_end with orientation along line_dir
    start_angle = math.atan2(line_dir[1], line_dir[0])
    pts3d = rotate_translate_pts2d(pts2d, (line_end[0], line_end[1]), start_angle)

    # clothoid end point
    end_pt = pts3d[-1, 0:2]

    # compute new arc start angle so that arc start point equals clothoid end
    vec = end_pt - np.array(arc_center)
    new_arc_start = math.atan2(vec[1], vec[0])

    # sample arc from new_arc_start to arc_end_angle adjusted by same delta (keep arc sweep length)
    # compute sweep preserving original sweep direction and length
    # original sweep
    orig_sweep = (arc_end_angle - arc_start_angle)
    # choose new end = new_start + orig_sweep
    new_arc_end = new_arc_start + orig_sweep

    arc_pts = sample_circle(arc_center, arc_R, new_arc_start, new_arc_end, n=200)

    # make poly wires
    # Ensure numerical coincidence: if sampled arc start differs from clothoid end,
    # force exact match to avoid tiny gaps in display/topology.
    end_pt_vec = np.array([pts3d[-1, 0], pts3d[-1, 1]])
    arc_start_vec = np.array([arc_pts[0, 0], arc_pts[0, 1]])
    diff = np.linalg.norm(end_pt_vec - arc_start_vec)
    if diff > 1e-6:
        # snap first arc sample to clothoid end, and snap clothoid last point to arc start
        arc_pts[0, 0] = float(end_pt_vec[0])
        arc_pts[0, 1] = float(end_pt_vec[1])
        pts3d[-1, 0] = float(end_pt_vec[0])
        pts3d[-1, 1] = float(end_pt_vec[1])

    # Build a shared TopoDS_Vertex for exact topological connection
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
    shared_pnt = gp_Pnt(float(pts3d[-1, 0]), float(pts3d[-1, 1]), 0.0)
    shared_vert = BRepBuilderAPI_MakeVertex(shared_pnt).Vertex()

    # Make wires reusing the shared vertex at the last index of clothoid and first of arc
    clothoid_wire = make_poly_wire_from_points_3d_with_shared(shared_vert, pts3d, shared_index=len(pts3d) - 1)
    arc_wire = make_poly_wire_from_points_3d_with_shared(shared_vert, arc_pts, shared_index=0)

    return clothoid_wire, arc_wire, pts3d, arc_center, new_arc_start, new_arc_end


if __name__ == '__main__':
    # example geometry
    line_end = np.array([0.0, 0.0])
    line_dir = np.array([1.0, 0.0])  # along +x
    arc_center = np.array([200.0, 80.0])
    arc_R = 50.0
    arc_start_angle = math.radians(160)
    arc_end_angle = math.radians(300)

    clothoid_wire, arc_wire, pts3d, center, a_start, a_end = connect_line_arc_with_clothoid(
        line_end, line_dir, arc_center, arc_R, arc_start_angle, arc_end_angle
    )

    display, start_display, _, _ = init_display()
    display.DisplayShape(clothoid_wire, update=True, color='BLUE')
    display.DisplayShape(arc_wire, update=True, color='GREEN')
    # show line as short segment before clothoid
    from OCC.Core.gp import gp_Pnt
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
    p0 = gp_Pnt(line_end[0] - 40 * line_dir[0], line_end[1] - 40 * line_dir[1], 0)
    p1 = gp_Pnt(line_end[0], line_end[1], 0)
    e = BRepBuilderAPI_MakeEdge(p0, p1).Edge()
    display.DisplayShape(e, update=True, color='RED')

    display.FitAll()
    start_display()
