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
from OCC.Core.Precision import precision
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Circ, gp_Dir

from OCC.Extend.ShapeFactory import make_edge, make_vertex
from OCCUtils.Construct import make_polygon, make_vertex, make_face


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
        "min": {"distance": None, "pairs": []},
        "max": {"distance": None, "pairs": []},
    }

    # Min (DistShapeShape)
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
    except Exception as e:
        print("compute_min_max_distance: min calculation failed:", e)

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
        except Exception:
            # fallback: try Value() if DistValue isn't present
            try:
                dmax = dss.Value()
            except Exception:
                dmax = dst0

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
    except Exception as e:
        print("compute_min_max_distance: max calculation failed:", e)
        # fallback to coarse guess
        result["max"]["distance"] = dst0
        if p_guess1 is not None and p_guess2 is not None:
            result["max"]["pairs"] = [(p_guess1, p_guess2)]

    return result


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
        gp_Ax2(gp_Pnt(1, 0, 2), gp_Dir(0, 0, 1)), 1.0, 1.0, 1.0
    ).Shape()

    display.DisplayShape([box1, box2], transparency=0.7)
    results = compute_min_max_distance(box1, box2)
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
