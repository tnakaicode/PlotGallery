#!/usr/bin/env python

# Copyright 2009-2015 Jelle Feringa (jelleferinga@gmail.com)
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

from __future__ import print_function

from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_DistanceSS
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.Extrema import Extrema_ExtFlag_MAX
from OCC.Core.Extrema import Extrema_ExtFlag_MIN
from OCC.Core.Precision import precision
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Circ, gp_Dir
import logging


from OCC.Extend.ShapeFactory import make_edge, make_vertex
from OCCUtils.Construct import make_polygon, make_vertex, make_face
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import topods
from OCC.Core.Geom import Geom_Plane
from OCC.Core.gp import gp_Vec

logger = logging.getLogger(__name__)


def make_bbox_for(shape, gap=1.0e-6):
    """Create and return a Bnd_Box for shape with a stable gap setting."""
    bnd = Bnd_Box()
    bnd.SetGap(gap)
    brepbndlib.Add(shape, bnd, True)
    return bnd


def _dss_value(dss):
    """Robustly obtain a numeric value from a DistanceSS-like object.

    Prefer DistValue(), then Value(). If neither exists, return None.
    """
    if hasattr(dss, "DistValue"):
        return dss.DistValue()
    if hasattr(dss, "Value"):
        return dss.Value()
    return None


def _dss_solutions(dss):
    """Try to extract point-pair solutions from a DistanceSS-like object.

    If the typical methods NbSolution/PointOnShape1/PointOnShape2 are
    available, use them. Otherwise return an empty list.
    """
    out = []

    # Try common API: NbSolution + PointOnShape1/2
    n = None
    for nb_name in ("NbSolution", "NbSolutions", "NbSol", "NbPnt"):
        if hasattr(dss, nb_name):
            n = int(getattr(dss, nb_name)())
            break

    if n is not None:
        for i in range(1, n + 1):
            for p1_name, p2_name in (
                ("PointOnShape1", "PointOnShape2"),
                ("PointOnS1", "PointOnS2"),
                ("PointOn1", "PointOn2"),
            ):
                if hasattr(dss, p1_name) and hasattr(dss, p2_name):
                    p1 = getattr(dss, p1_name)(i)
                    p2 = getattr(dss, p2_name)(i)
                    out.append((p1, p2))
                    break
        if out:
            return out

    # Next, try Solution-style methods that might return tuples
    for attr in dir(dss):
        if "Solution" in attr or "solution" in attr:
            func = getattr(dss, attr)
            if callable(func):
                for i in range(1, 11):
                    res = func(i)
                    if isinstance(res, tuple) and len(res) >= 2:
                        out.append((res[0], res[1]))
                    else:
                        if hasattr(res, "Value"):
                            val = res.Value()
                            if isinstance(val, tuple) and len(val) >= 2:
                                out.append((val[0], val[1]))
                if out:
                    return out

    logger.debug(
        "Unable to extract solutions from DistanceSS-like object; available attrs: %s",
        dir(dss),
    )
    return out


def detect_continuous_pairs(pairs, dval, shape1, shape2, tol=1e-6):
    """Heuristic detection whether a list of point-pairs represents a
    continuous (infinite) set of minimal/maximal solutions.

    The heuristic checks face-face planar cases: if a pair lies on two
    planar faces whose supporting planes are parallel and the plane
    distance equals dval (within tol), and their projected 2D bboxes
    overlap, the solution is marked as continuous (area or line).
    """
    is_cont = False
    cont_type = None
    if dval is None or not pairs:
        return {"is_continuous": False, "continuity_type": None}

    def faces_containing_point(shape, pnt):
        faces = []
        exp = TopExp_Explorer(shape, TopAbs_FACE)
        while exp.More():
            f = topods.Face(exp.Current())
            bnd = Bnd_Box()
            bnd.SetGap(1.0e-6)
            brepbndlib.Add(f, bnd, True)
            xmin, ymin, zmin, xmax, ymax, zmax = bnd.Get()
            x, y, z = pnt.X(), pnt.Y(), pnt.Z()
            if (
                (xmin - tol <= x <= xmax + tol)
                and (ymin - tol <= y <= ymax + tol)
                and (zmin - tol <= z <= zmax + tol)
            ):
                faces.append(f)
            exp.Next()
        return faces

    for p1, p2 in pairs:
        f1_list = faces_containing_point(shape1, p1)
        f2_list = faces_containing_point(shape2, p2)
        for f1 in f1_list:
            for f2 in f2_list:
                surf1 = BRep_Tool.Surface(f1)
                surf2 = BRep_Tool.Surface(f2)
                pl1 = Geom_Plane.DownCast(surf1)
                pl2 = Geom_Plane.DownCast(surf2)
                if pl1 is None or pl2 is None:
                    continue
                # get normals as gp_Vec
                n1 = pl1.Axis().Direction()
                n2 = pl2.Axis().Direction()
                # check parallel
                if not n1.IsParallel(n2, tol):
                    continue
                # compute distance between planes: project origin of pl2 onto pl1
                p_loc1 = pl1.Location()
                p_loc2 = pl2.Location()
                vec = gp_Vec(p_loc1, p_loc2)
                dist_planes = abs(vec.Dot(gp_Vec(n1.X(), n1.Y(), n1.Z())))
                if abs(dist_planes - dval) > max(tol, abs(dval) * 1e-6):
                    continue

                # get bbox corners for both faces and project onto plane axes
                b1 = Bnd_Box()
                b1.SetGap(1.0e-6)
                brepbndlib.Add(f1, b1, True)
                b2 = Bnd_Box()
                b2.SetGap(1.0e-6)
                brepbndlib.Add(f2, b2, True)
                xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = b1.Get()
                xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = b2.Get()
                corners1 = [
                    gp_Pnt(x, y, z)
                    for x in (xmin1, xmax1)
                    for y in (ymin1, ymax1)
                    for z in (zmin1, zmax1)
                ]
                corners2 = [
                    gp_Pnt(x, y, z)
                    for x in (xmin2, xmax2)
                    for y in (ymin2, ymax2)
                    for z in (zmin2, zmax2)
                ]

                nvec = gp_Vec(n1.X(), n1.Y(), n1.Z())
                arb = gp_Vec(1.0, 0.0, 0.0)
                if abs(nvec.Dot(arb)) > 0.9:
                    arb = gp_Vec(0.0, 1.0, 0.0)
                u = nvec.Crossed(arb)
                if u.Magnitude() == 0:
                    continue
                u = u.Normalized()
                v = nvec.Crossed(u).Normalized()

                def proj_points(corners):
                    us = []
                    vs = []
                    for c in corners:
                        vec_c = gp_Vec(p_loc1, c)
                        us.append(vec_c.Dot(u))
                        vs.append(vec_c.Dot(v))
                    return min(us), max(us), min(vs), max(vs)

                u1min, u1max, v1min, v1max = proj_points(corners1)
                u2min, u2max, v2min, v2max = proj_points(corners2)

                overlap_u = not (u1max < u2min - tol or u2max < u1min - tol)
                overlap_v = not (v1max < v2min - tol or v2max < v1min - tol)
                if overlap_u and overlap_v:
                    is_cont = True
                    cont_type = "area"
                    break
                elif overlap_u or overlap_v:
                    is_cont = True
                    cont_type = "line"
                    break
            if is_cont:
                break
        if is_cont:
            break

    return {"is_continuous": is_cont, "continuity_type": cont_type}


def bbox_corner_candidates(shape):
    """Return the 8 corner points of the bounding box of a shape."""
    bnd = Bnd_Box()
    bnd.SetGap(1.0e-6)
    brepbndlib.Add(shape, bnd, True)
    xmin, ymin, zmin, xmax, ymax, zmax = bnd.Get()
    corners = [
        gp_Pnt(x, y, z)
        for x in (xmin, xmax)
        for y in (ymin, ymax)
        for z in (zmin, zmax)
    ]
    return corners


def coarse_max_by_bbox(shape1, shape2):
    """Compute a coarse maximal distance and a candidate point-pair using bbox corners."""
    c1 = bbox_corner_candidates(shape1)
    c2 = bbox_corner_candidates(shape2)
    maxd = 0.0
    pair = (None, None)
    for p1 in c1:
        for p2 in c2:
            d = p1.Distance(p2)
            if d > maxd:
                maxd = d
                pair = (p1, p2)
    return maxd, pair


def is_point_bbox_corner(shape, pnt, tol=1e-6):
    """Return True if pnt is (approximately) one of the bbox corner points of shape."""
    corners = bbox_corner_candidates(shape)
    for c in corners:
        if c.Distance(pnt) <= tol:
            return True
    return False


def compute_min_max_distance(shape1, shape2, maxiter=100):
    """Compute minimal and maximal distances between two TopoDS_Shape objects.

    Returns a dict with keys 'min' and 'max', each containing:
      - distance: float or None
      - pairs: list of (gp_Pnt, gp_Pnt) candidate point pairs

    Notes:
      - For min we use BRepExtrema_DistShapeShape.
      - For max we use a bbox-corner coarse guess and BRepExtrema_DistanceSS
        with Extrema_ExtFlag_MAX where available. If precise extraction of
        point pairs fails, the coarse bbox pair is returned as fallback.
    """
    result = {
        "min": {"distance": None, "pairs": [], "source": None},
        "max": {"distance": None, "pairs": [], "source": None},
    }

    # Min: attempt DistanceSS(min) if available; otherwise fallback to DistShapeShape
    # Build bboxes once using helper
    bnd1 = make_bbox_for(shape1)
    bnd2 = make_bbox_for(shape2)

    # attempt DistanceSS for minimum if class is available
    if BRepExtrema_DistanceSS is not None:
        ub, _ = coarse_max_by_bbox(shape1, shape2)
        dss_min = BRepExtrema_DistanceSS(
            shape1,
            shape2,
            bnd1,
            bnd2,
            ub,
            precision.Confusion(),
            Extrema_ExtFlag_MIN,
            maxiter,
        )
        dmin = _dss_value(dss_min)
        pairs = _dss_solutions(dss_min)
        if dmin is not None:
            # Keep numeric value from DistanceSS
            result["min"]["distance"] = dmin
            # If DistanceSS did not return point pairs, fallback to
            # BRepExtrema_DistShapeShape to extract representative pairs.
            if pairs:
                result["min"]["pairs"] = pairs
                result["min"]["source"] = "DistanceSS"
            else:
                # Fallback extractor: use DistShapeShape just to get point pairs
                dss_fb = BRepExtrema_DistShapeShape()
                dss_fb.LoadS1(shape1)
                dss_fb.LoadS2(shape2)
                dss_fb.Perform()
                fb_pairs = []
                if dss_fb.IsDone():
                    try:
                        nsol = int(dss_fb.NbSolution())
                    except Exception:
                        nsol = 0
                    for i in range(1, nsol + 1):
                        p1 = dss_fb.PointOnShape1(i)
                        p2 = dss_fb.PointOnShape2(i)
                        fb_pairs.append((p1, p2))
                if fb_pairs:
                    result["min"]["pairs"] = fb_pairs
                    result["min"]["source"] = "DistanceSS+DistShapeShape"
                else:
                    # keep empty pairs but record source as DistanceSS
                    result["min"]["pairs"] = []
                    result["min"]["source"] = "DistanceSS"

    # fallback to BRepExtrema_DistShapeShape when needed
    if result["min"]["distance"] is None:
        dss = BRepExtrema_DistShapeShape()
        dss.LoadS1(shape1)
        dss.LoadS2(shape2)
        dss.Perform()
        if dss.IsDone():
            dmin = dss.Value()
            pairs = []
            nsol = int(dss.NbSolution())
            for i in range(1, nsol + 1):
                p1 = dss.PointOnShape1(i)
                p2 = dss.PointOnShape2(i)
                pairs.append((p1, p2))
            result["min"]["distance"] = dmin
            result["min"]["pairs"] = pairs
            result["min"]["source"] = "DistShapeShape"

    # mark whether min pairs come from bbox corners
    min_flags = []
    for p1, p2 in result["min"]["pairs"]:
        f1 = is_point_bbox_corner(shape1, p1)
        f2 = is_point_bbox_corner(shape2, p2)
        min_flags.append((f1, f2))
    result["min"]["pairs_from_bbox"] = min_flags

    # detect continuity of min solutions (heuristic)
    cont_min = detect_continuous_pairs(result["min"]["pairs"], result["min"]["distance"], shape1, shape2)
    result["min"]["is_continuous"] = cont_min.get("is_continuous", False)
    result["min"]["continuity_type"] = cont_min.get("continuity_type", None)

    # Max (bbox coarse guess + DistanceSS with MAX flag)
    # Max: coarse bbox initial guess, then try DistanceSS(MAX)
    dst0, (p_guess1, p_guess2) = coarse_max_by_bbox(shape1, shape2)

    # ensure we have bnd boxes (re-use if available)
    bnd1 = make_bbox_for(shape1) if "bnd1" not in locals() or bnd1 is None else bnd1
    bnd2 = make_bbox_for(shape2) if "bnd2" not in locals() or bnd2 is None else bnd2

    if BRepExtrema_DistanceSS is not None:
        dss = BRepExtrema_DistanceSS(
            shape1,
            shape2,
            bnd1,
            bnd2,
            dst0,
            precision.Confusion(),
            Extrema_ExtFlag_MAX,
            maxiter,
        )
        dmax = _dss_value(dss)
        pairs = _dss_solutions(dss)
        # fallback to bbox pair if no points extracted
        if not pairs and p_guess1 is not None and p_guess2 is not None:
            pairs = [(p_guess1, p_guess2)]
        if dmax is None:
            # if we couldn't get a numeric value, use the bbox guess
            dmax = dst0
            src = "bbox"
        else:
            src = "DistanceSS"
        result["max"]["distance"] = dmax
        result["max"]["pairs"] = pairs
        result["max"]["source"] = src
    else:
        # no DistanceSS available; return bbox guess
        result["max"]["distance"] = dst0
        result["max"]["pairs"] = [(p_guess1, p_guess2)] if p_guess1 is not None else []
        result["max"]["source"] = "bbox"

    # mark whether max pairs come from bbox corners
    max_flags = []
    for p1, p2 in result["max"]["pairs"]:
        f1 = is_point_bbox_corner(shape1, p1)
        f2 = is_point_bbox_corner(shape2, p2)
        max_flags.append((f1, f2))
    result["max"]["pairs_from_bbox"] = max_flags

    # detect continuity for max solutions as well
    cont_max = detect_continuous_pairs(result["max"]["pairs"], result["max"]["distance"], shape1, shape2)
    result["max"]["is_continuous"] = cont_max.get("is_continuous", False)
    result["max"]["continuity_type"] = cont_max.get("continuity_type", None)

    return result


def detect_continuous_minima(result, shape1, shape2, tol=1e-6):
    """Heuristic detection whether the minimal-distance solution is continuous.

    This implements a face-face plane check: if the minimal pair lies on two
    planar faces whose supporting planes are parallel and the plane distance
    equals dmin (within tol), and their projected 2D bboxes overlap, we mark
    the minimum as continuous (area or line).
    """
    is_cont = False
    cont_type = None
    if result["min"]["distance"] is None:
        return {"is_continuous": False, "continuity_type": None}

    dmin = result["min"]["distance"]

    # collect faces whose bbox contains the point
    def faces_containing_point(shape, pnt):
        faces = []
        exp = TopExp_Explorer(shape, TopAbs_FACE)
        while exp.More():
            f = topods.Face(exp.Current())
            bnd = Bnd_Box()
            bnd.SetGap(1.0e-6)
            brepbndlib.Add(f, bnd, True)
            xmin, ymin, zmin, xmax, ymax, zmax = bnd.Get()
            x, y, z = pnt.X(), pnt.Y(), pnt.Z()
            if (
                (xmin - tol <= x <= xmax + tol)
                and (ymin - tol <= y <= ymax + tol)
                and (zmin - tol <= z <= zmax + tol)
            ):
                faces.append(f)
            exp.Next()
        return faces

    for p1, p2 in result["min"]["pairs"]:
        f1_list = faces_containing_point(shape1, p1)
        f2_list = faces_containing_point(shape2, p2)
        for f1 in f1_list:
            for f2 in f2_list:
                surf1 = BRep_Tool.Surface(f1)
                surf2 = BRep_Tool.Surface(f2)
                pl1 = Geom_Plane.DownCast(surf1)
                pl2 = Geom_Plane.DownCast(surf2)
                if pl1 is None or pl2 is None:
                    continue
                # get normals as gp_Vec
                n1 = pl1.Axis().Direction()
                n2 = pl2.Axis().Direction()
                # check parallel
                if not n1.IsParallel(n2, tol):
                    continue
                # compute distance between planes: project origin of pl2 onto pl1
                # use locations
                p_loc1 = pl1.Location()
                p_loc2 = pl2.Location()
                vec = gp_Vec(p_loc1, p_loc2)
                # signed distance along normal
                dist_planes = abs(vec.Dot(gp_Vec(n1.X(), n1.Y(), n1.Z())))
                if abs(dist_planes - dmin) > max(tol, abs(dmin) * 1e-6):
                    continue

                # get bbox corners for both faces and project onto plane axes
                b1 = Bnd_Box()
                b1.SetGap(1.0e-6)
                brepbndlib.Add(f1, b1, True)
                b2 = Bnd_Box()
                b2.SetGap(1.0e-6)
                brepbndlib.Add(f2, b2, True)
                xmin1, ymin1, zmin1, xmax1, ymax1, zmax1 = b1.Get()
                xmin2, ymin2, zmin2, xmax2, ymax2, zmax2 = b2.Get()
                corners1 = [
                    gp_Pnt(x, y, z)
                    for x in (xmin1, xmax1)
                    for y in (ymin1, ymax1)
                    for z in (zmin1, zmax1)
                ]
                corners2 = [
                    gp_Pnt(x, y, z)
                    for x in (xmin2, xmax2)
                    for y in (ymin2, ymax2)
                    for z in (zmin2, zmax2)
                ]

                # build local axes on plane: n1 is normal; pick arbitrary u
                nvec = gp_Vec(n1.X(), n1.Y(), n1.Z())
                arb = gp_Vec(1.0, 0.0, 0.0)
                if abs(nvec.Dot(arb)) > 0.9:
                    arb = gp_Vec(0.0, 1.0, 0.0)
                u = nvec.Crossed(arb)
                if u.Magnitude() == 0:
                    continue
                u = u.Normalized()
                v = nvec.Crossed(u).Normalized()

                def proj_points(corners):
                    us = []
                    vs = []
                    for c in corners:
                        vec_c = gp_Vec(p_loc1, c)
                        us.append(vec_c.Dot(u))
                        vs.append(vec_c.Dot(v))
                    return min(us), max(us), min(vs), max(vs)

                u1min, u1max, v1min, v1max = proj_points(corners1)
                u2min, u2max, v2min, v2max = proj_points(corners2)

                # check overlap in u and v ranges
                overlap_u = not (u1max < u2min - tol or u2max < u1min - tol)
                overlap_v = not (v1max < v2min - tol or v2max < v1min - tol)
                if overlap_u and overlap_v:
                    # area overlap
                    is_cont = True
                    cont_type = "area"
                    break
                elif overlap_u or overlap_v:
                    is_cont = True
                    cont_type = "line"
                    break
            if is_cont:
                break
        if is_cont:
            break

    return {"is_continuous": is_cont, "continuity_type": cont_type}


if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()

    def f1(x, y):
        return x, y, 1.0 * x + 2.0 * y

    def f2(x, y):
        return x, y, 0.5 * x + 0.1 * y - 1.0

    face1 = make_face(
        make_polygon(
            [
                gp_Pnt(*f1(0.0, 0.0)),
                gp_Pnt(*f1(0.1, 0.1)),
                gp_Pnt(*f1(0.0, 0.2)),
                gp_Pnt(*f1(-0.1, 0.1)),
            ],
            closed=True,
        )
    )
    box1 = BRepPrimAPI_MakeBox(
        gp_Ax2(gp_Pnt(1, 0, 0), gp_Dir(0, 0, 1)), 1.0, 1.0, 1.0
    ).Shape()

    box2 = BRepPrimAPI_MakeBox(
        gp_Ax2(gp_Pnt(1.5-1, 0.5-1, 2), gp_Dir(0, 0.0, 1)), 2.0, 2.0, 2.0
    ).Shape()

    shapes = [box1, box2]

    display.DisplayShape(shapes, transparency=0.7)
    results = compute_min_max_distance(*shapes)
    print(results["min"])
    print(results["max"])
    [
        display.DisplayShape(make_edge(p1, p2), color="GREEN")
        for p1, p2 in results["min"]["pairs"]
    ]
    [
        display.DisplayShape(make_edge(p1, p2), color="BLUE1")
        for p1, p2 in results["max"]["pairs"]
    ]
    display.DisplayShape(gp_Pnt())

    display.FitAll()
    start_display()
