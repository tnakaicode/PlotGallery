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

from OCC.Extend.ShapeFactory import make_edge, make_vertex
from OCCUtils.Construct import make_polygon, make_vertex, make_face
from OCC.Core.BRep import BRep_Tool
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import topods
from OCC.Core.Geom import Geom_Plane
from OCC.Core.gp import gp_Vec


def bbox_corner_candidates(shape):
    """Return the 8 corner points of the bounding box of a shape."""
    bnd = Bnd_Box()
    bnd.SetGap(1.0e-6)
    brepbndlib.Add(shape, bnd, True)
    try:
        xmin, ymin, zmin, xmax, ymax, zmax = bnd.Get()
    except Exception:
        # fallback: try to get values via tuple
        vals = bnd.Get()
        xmin, ymin, zmin, xmax, ymax, zmax = vals
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
    try:
        corners = bbox_corner_candidates(shape)
    except Exception:
        return False
    for c in corners:
        try:
            if c.Distance(pnt) <= tol:
                return True
        except Exception:
            pass
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

    # Min: either try DistanceSS (optional) or fallback to DistShapeShape
    try:
        # prepare bounding boxes
        bnd1 = Bnd_Box()
        bnd1.SetGap(1.0e-6)
        brepbndlib.Add(shape1, bnd1, True)
        bnd2 = Bnd_Box()
        bnd2.SetGap(1.0e-6)
        brepbndlib.Add(shape2, bnd2, True)

        # use bbox coarse max as an initial upper bound for the search
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
        try:
            dmin = dss_min.DistValue()
        except Exception:
            try:
                dmin = dss_min.Value()
            except Exception:
                dmin = None

        pairs = []
        try:
            n = dss_min.NbSolution()
            for i in range(1, n + 1):
                try:
                    p1 = dss_min.PointOnShape1(i)
                    p2 = dss_min.PointOnShape2(i)
                    pairs.append((p1, p2))
                except Exception:
                    pass
        except Exception:
            pass

        if dmin is not None:
            result["min"]["distance"] = dmin
            result["min"]["pairs"] = pairs
            result["min"]["source"] = "DistanceSS"
    except Exception as e:
        print("compute_min_max_distance: DistanceSS(min) attempt failed:", e)

    if result["min"]["distance"] is None:
        try:
            dss = BRepExtrema_DistShapeShape()
            dss.LoadS1(shape1)
            dss.LoadS2(shape2)
            dss.Perform()
            if dss.IsDone():
                dmin = dss.Value()
                pairs = []
                for i in range(1, dss.NbSolution() + 1):
                    try:
                        p1 = dss.PointOnShape1(i)
                        p2 = dss.PointOnShape2(i)
                        pairs.append((p1, p2))
                    except Exception:
                        # skip if shape-specific extraction fails
                        pass
                result["min"]["distance"] = dmin
                result["min"]["pairs"] = pairs
                result["min"]["source"] = "DistShapeShape"
        except Exception as e:
            print("compute_min_max_distance: min calculation failed:", e)

    # mark whether min pairs come from bbox corners
    try:
        min_flags = []
        for p1, p2 in result["min"]["pairs"]:
            f1 = is_point_bbox_corner(shape1, p1)
            f2 = is_point_bbox_corner(shape2, p2)
            min_flags.append((f1, f2))
        result["min"]["pairs_from_bbox"] = min_flags
    except Exception:
        result["min"]["pairs_from_bbox"] = []

    # detect continuity of min solutions (heuristic)
    try:
        cont = detect_continuous_minima(result, shape1, shape2)
        result["min"]["is_continuous"] = cont.get("is_continuous", False)
        result["min"]["continuity_type"] = cont.get("continuity_type", None)
    except Exception:
        result["min"]["is_continuous"] = False
        result["min"]["continuity_type"] = None

    # Max (bbox coarse guess + DistanceSS with MAX flag)
    try:
        dst0, (p_guess1, p_guess2) = coarse_max_by_bbox(shape1, shape2)
    except Exception as e:
        print("compute_min_max_distance: bbox coarse guess failed:", e)
        dst0 = 0.0
        p_guess1 = p_guess2 = None

    try:
        bnd1 = Bnd_Box()
        bnd1.SetGap(1.0e-6)
        brepbndlib.Add(shape1, bnd1, True)
        bnd2 = Bnd_Box()
        bnd2.SetGap(1.0e-6)
        brepbndlib.Add(shape2, bnd2, True)

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
        try:
            dmax = dss.DistValue()
            result["max"]["source"] = "DistanceSS"
        except Exception:
            # fallback: try Value() if DistValue isn't present
            try:
                dmax = dss.Value()
                result["max"]["source"] = "DistanceSS"
            except Exception:
                dmax = dst0
                # mark that we fell back to bbox
                result["max"]["source"] = "bbox"

        pairs = []
        # try to extract point solutions if API provides them
        try:
            n = dss.NbSolution()
            for i in range(1, n + 1):
                try:
                    p1 = dss.PointOnShape1(i)
                    p2 = dss.PointOnShape2(i)
                    pairs.append((p1, p2))
                except Exception:
                    pass
        except Exception:
            # some DistanceSS variants don't expose NbSolution/PointOnShape methods
            pass

        if not pairs and p_guess1 is not None and p_guess2 is not None:
            pairs = [(p_guess1, p_guess2)]

        result["max"]["distance"] = dmax
        result["max"]["pairs"] = pairs
        # if DistanceSS returned same as bbox guess but source not set, set it
        if result["max"]["source"] is None:
            # if the computed dmax equals bbox dst0 within tolerance, mark bbox
            try:
                if abs(dmax - dst0) < 1e-9:
                    result["max"]["source"] = "bbox"
                else:
                    result["max"]["source"] = "DistanceSS"
            except Exception:
                result["max"]["source"] = "DistanceSS"
    except Exception as e:
        print("compute_min_max_distance: max calculation failed:", e)
        # fallback to coarse guess
        result["max"]["distance"] = dst0
        # mark bbox as source in fallback
        result["max"]["source"] = "bbox"
        if p_guess1 is not None and p_guess2 is not None:
            result["max"]["pairs"] = [(p_guess1, p_guess2)]

    # mark whether max pairs come from bbox corners
    try:
        max_flags = []
        for p1, p2 in result["max"]["pairs"]:
            f1 = is_point_bbox_corner(shape1, p1)
            f2 = is_point_bbox_corner(shape2, p2)
            max_flags.append((f1, f2))
        result["max"]["pairs_from_bbox"] = max_flags
    except Exception:
        result["max"]["pairs_from_bbox"] = []

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
            try:
                brepbndlib.Add(f, bnd, True)
                xmin, ymin, zmin, xmax, ymax, zmax = bnd.Get()
                x, y, z = pnt.X(), pnt.Y(), pnt.Z()
                if (
                    (xmin - tol <= x <= xmax + tol)
                    and (ymin - tol <= y <= ymax + tol)
                    and (zmin - tol <= z <= zmax + tol)
                ):
                    faces.append(f)
            except Exception:
                pass
            exp.Next()
        return faces

    for p1, p2 in result["min"]["pairs"]:
        f1_list = faces_containing_point(shape1, p1)
        f2_list = faces_containing_point(shape2, p2)
        for f1 in f1_list:
            for f2 in f2_list:
                try:
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
                except Exception:
                    continue
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
        gp_Ax2(gp_Pnt(1, 0.5, 2), gp_Dir(0, 0.0, 1)), 2.0, 2.0, 2.0
    ).Shape()

    shapes = [box1, box2]

    display.DisplayShape(shapes, transparency=0.7)
    results = compute_min_max_distance(*shapes)
    print(results)
    [
        display.DisplayShape(make_edge(p1, p2), color="GREEN")
        for p1, p2 in results["min"]["pairs"]
    ]
    [
        display.DisplayShape(make_edge(p1, p2), color="BLUE1")
        for p1, p2 in results["max"]["pairs"]
    ]

    display.FitAll()
    start_display()
