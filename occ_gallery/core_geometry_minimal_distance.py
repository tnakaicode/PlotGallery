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
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Circ

from OCC.Extend.ShapeFactory import make_edge, make_vertex

display, start_display, add_menu, add_function_to_menu = init_display()


def compute_minimal_distance_between_cubes():
    """compute the minimal distance between 2 cubes

    the line between the 2 points is rendered in cyan

    """
    b1 = BRepPrimAPI_MakeBox(gp_Pnt(100, 0, 0), 10.0, 10.0, 10.0).Shape()
    b2 = BRepPrimAPI_MakeBox(gp_Pnt(45, 45, 45), 10.0, 10.0, 10.0).Shape()
    display.DisplayShape([b1, b2], transparency=0.7)

    dss = BRepExtrema_DistShapeShape()
    dss.LoadS1(b1)
    dss.LoadS2(b2)
    dss.Perform()

    assert dss.IsDone()

    print("Minimal distance between cubes: ", dss.Value())

    edg = make_edge(dss.PointOnShape1(1), dss.PointOnShape2(1))
    display.DisplayColoredShape([edg], color="CYAN")


def compute_minimal_distance_between_circles():
    """compute the minimal distance between 2 circles

    here the minimal distance overlaps the intersection of the circles
    the points are rendered to indicate the locations

    """
    # required for precise rendering of the circles
    display.Context.SetDeviationCoefficient(0.0001)
    L = gp_Pnt(4, 10, 0)
    M = gp_Pnt(10, 16, 0)

    Laxis = gp_Ax2()
    Maxis = gp_Ax2()
    Laxis.SetLocation(L)
    Maxis.SetLocation(M)

    r1 = 12.0
    r2 = 15.0
    Lcircle = gp_Circ(Laxis, r1)
    Mcircle = gp_Circ(Maxis, r2)

    l_circle, m_circle = make_edge(Lcircle), make_edge(Mcircle)
    display.DisplayShape([l_circle, m_circle])

    # compute the minimal distance between 2 circles
    # the minimal distance here matches the intersection of the circles
    dss = BRepExtrema_DistShapeShape(l_circle, m_circle)

    print(
        "intersection parameters on l_circle:",
        [dss.ParOnEdgeS1(i) for i in range(1, dss.NbSolution() + 1)],
    )
    print(
        "intersection parameters on m_circle:",
        [dss.ParOnEdgeS2(i) for i in range(1, dss.NbSolution() + 1)],
    )

    for i in range(1, dss.NbSolution() + 1):
        pnt = dss.PointOnShape1(i)
        display.DisplayShape(make_vertex(pnt))


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


def compute_maximal_distance_demo():
    """Demo: compute maximal distance between two boxes using bbox guess + DistanceSS (MAX).

    This is a lightweight implementation: the precise step uses BRepExtrema_DistanceSS
    with Extrema_ExtFlag_MAX to try to locate the global maximum (given a good initial
    distance estimate from the bbox corners).
    """
    b1 = BRepPrimAPI_MakeBox(gp_Pnt(0, 0, 0), 20.0, 10.0, 10.0).Shape()
    b2 = BRepPrimAPI_MakeBox(gp_Pnt(50, 30, 5), 5.0, 40.0, 8.0).Shape()
    display.DisplayShape([b1, b2], transparency=0.7)

    # coarse guess via bounding-box corners
    dst0, (p_guess1, p_guess2) = coarse_max_by_bbox(b1, b2)
    print("Coarse max (bbox corners):", dst0)

    # prepare bounding boxes for DistanceSS
    bnd1 = Bnd_Box()
    bnd1.SetGap(1.0e-6)
    brepbndlib.Add(b1, bnd1, True)
    bnd2 = Bnd_Box()
    bnd2.SetGap(1.0e-6)
    brepbndlib.Add(b2, bnd2, True)

    # call DistanceSS with MAX flag
    try:
        dss = BRepExtrema_DistanceSS(
            b1, b2, bnd1, bnd2, dst0, precision.Confusion(), Extrema_ExtFlag_MAX, 100
        )
        dval = dss.DistValue()
        print("Precise max (DistanceSS):", dval)
    except Exception as e:
        print("DistanceSS MAX failed:", e)
        dval = dst0

    # draw the coarse candidate pair for visualization
    if p_guess1 is not None and p_guess2 is not None:
        edg = make_edge(p_guess1, p_guess2)
        display.DisplayShape(edg)

    return dval


if __name__ == "__main__":
    compute_minimal_distance_between_cubes()
    compute_minimal_distance_between_circles()
    compute_maximal_distance_demo()
    display.FitAll()
    start_display()
