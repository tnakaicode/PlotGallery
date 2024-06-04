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

from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape, BRepExtrema_DistanceSS, BRepExtrema_ExtPF, BRepExtrema_ExtFF
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.Extrema import Extrema_ExtFlag_MAX, Extrema_ExtFlag_MIN
from OCC.Core.Extrema import Extrema_ExtAlgo_Grad
from OCC.Core.Precision import precision
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Ax2, gp_Circ

from OCC.Extend.ShapeFactory import make_edge, make_vertex, get_boundingbox, make_face
from OCCUtils.Construct import make_polygon, make_vertex

display, start_display, add_menu, add_function_to_menu = init_display()


def compute_maximal_distance_between_planes():
    """compute the minimal distance between 2 planes

    """
    def f1(x, y): return x, y, 1.0 * x + 2.0 * y
    def f2(x, y): return x, y, 0.5 * x + 0.1 * y - 1.0
    face1 = make_face(make_polygon([gp_Pnt(*f1(0.0, 0.0)),
                                    gp_Pnt(*f1(0.1, 0.1)),
                                    gp_Pnt(*f1(0.0, 0.2)),
                                    gp_Pnt(*f1(-0.1, 0.1)),
                                    ], closed=True))
    bnd1 = Bnd_Box()
    bnd1.SetGap(1.0e-6)
    brepbndlib.Add(face1, bnd1, True)
    face2 = make_face(make_polygon([gp_Pnt(*f2(0.0, 0.0)),
                                    gp_Pnt(*f2(0.1, 0.1)),
                                    gp_Pnt(*f2(0.0, 0.2)),
                                    gp_Pnt(*f2(-0.1, 0.1)),
                                    ], closed=True))
    bnd2 = Bnd_Box()
    bnd2.SetGap(1.0e-6)
    brepbndlib.Add(face2, bnd2, True)

    p1 = gp_Pnt(-0.1, -0.1, 0.0)
    v1 = make_vertex(p1)
    bndv = Bnd_Box()
    bndv.SetGap(1.0e-6)
    brepbndlib.Add(v1, bndv, True)

    display.DisplayShape(face1)
    display.DisplayShape(face2)

    dss = BRepExtrema_DistShapeShape()
    dss.LoadS1(v1)
    dss.LoadS2(face2)
    dss.Perform()

    edg = make_edge(dss.PointOnShape1(1), dss.PointOnShape2(1))
    dst = dss.Value()
    print(dst)
    display.DisplayShape(edg, color="RED")

    dss = BRepExtrema_DistanceSS(v1, face2,
                                 bndv, bnd2,
                                 dst, precision.Confusion(),
                                 Extrema_ExtFlag_MAX, 1)
    # print(dss.Seq1Value())
    print(dss.DistValue())

    dss = BRepExtrema_ExtFF(face1, face2)
    dss.Perform(face1, face2)
    print(dss.IsDone())
    print(dss.NbExt())
    print(dss.SquareDistance(1))


def compute_minimal_distance_between_cubes():
    """compute the minimal distance between 2 cubes

    the line between the 2 points is rendered in cyan

    """
    b1 = BRepPrimAPI_MakeBox(gp_Pnt(100, 0, 0), 10.0, 10.0, 10.0).Shape()
    b2 = BRepPrimAPI_MakeBox(gp_Pnt(45, 45, 45), 10.0, 10.0, 10.0).Shape()
    display.DisplayShape([b1, b2])

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


if __name__ == "__main__":
    compute_maximal_distance_between_planes()
    display.FitAll()
    start_display()
