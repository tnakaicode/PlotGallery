#!/usr/bin/env python

# Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
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

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Circ, gp_ZOX
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


def pipe():
    # the bspline path, must be a wire
    array2 = TColgp_Array1OfPnt(1, 3)
    array2.SetValue(1, gp_Pnt(0, 0, 0))
    array2.SetValue(2, gp_Pnt(0, 1, 2))
    array2.SetValue(3, gp_Pnt(0, 2, 3))
    bspline2 = GeomAPI_PointsToBSpline(array2).Curve()
    path_edge = BRepBuilderAPI_MakeEdge(bspline2).Edge()
    path_wire = BRepBuilderAPI_MakeWire(path_edge).Wire()

    # the bspline profile. Profile mist be a wire
    array = TColgp_Array1OfPnt(1, 5)
    array.SetValue(1, gp_Pnt(0, 0, 0))
    array.SetValue(2, gp_Pnt(1, 2, 0))
    array.SetValue(3, gp_Pnt(2, 3, 0))
    array.SetValue(4, gp_Pnt(4, 3, 0))
    array.SetValue(5, gp_Pnt(5, 5, 0))
    bspline = GeomAPI_PointsToBSpline(array).Curve()
    profile_edge = BRepBuilderAPI_MakeEdge(bspline).Edge()

    # pipe
    pipe = BRepOffsetAPI_MakePipe(path_wire, profile_edge).Shape()

    display.DisplayShape(profile_edge, update=False)
    display.DisplayShape(path_wire, update=False)
    display.DisplayShape(pipe, update=True)


def execute(points):
    # Creation of points for the spine
    # source: https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_topology_pipe.py
    from OCC.Core.TColgp import TColgp_Array1OfPnt
    from OCC.Core.Geom import Geom_BezierCurve, Geom_BSplineCurve, Geom_Circle
    from OCC.Core.GeomFill import GeomFill_Pipe
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeShell
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
    from OCC.Core.Law import Law_Linear
    length = len(points)
    array = TColgp_Array1OfPnt(0, length)
    for index in range(length):
        point = points[index]
        print(point)
        array.SetValue(index, gp_Pnt(point[0], point[1], point[2]))

    # Creation of a Bezier Curve as the spine
    bz_curv = Geom_BezierCurve(array)
    bz_curv_edge = BRepBuilderAPI_MakeEdge(bz_curv).Edge()
    bz_curv_wire = BRepBuilderAPI_MakeWire(bz_curv_edge).Wire()

    # Creation of profile to sweep along the spine
    radius = 1.60
    circle = gp_Circ(gp_ZOX(), radius)
    circle_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    circle_wire = BRepBuilderAPI_MakeWire(circle_edge).Wire()

    # Creation of the law to dictate the evolution of the profile
    brep1 = BRepOffsetAPI_MakePipeShell(bz_curv_wire)
    law_f = Law_Linear()
    law_f.Set(0, 1, 1, 1)
    brep1.SetLaw(circle_wire, law_f, True, True)
    brep1.Build()
    brep1.MakeSolid()
    return brep1.Shape()


def generate_2(points):
    # https://github.com/tpaviot/pythonocc-core/issues/1245
    # ref: https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_geometry_make_pipe_shell.py
    # convert points into a TColgp_Array1OfPnt into a bezier curve into a pipe
    from OCC.Core.TColgp import TColgp_Array1OfPnt
    from OCC.Core.Geom import Geom_BezierCurve, Geom_BSplineCurve, Geom_Circle
    from OCC.Core.GeomFill import GeomFill_Pipe
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeShell
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipeShell
    from OCC.Core.Law import Law_Linear

    length = len(points)
    poles = TColgp_Array1OfPnt(0, length)
    for i in range(length):
        point = gp_Pnt(points[i][0], points[i][1], points[i][2])
        display.DisplayShape(point)
        poles.SetValue(i, point)

    bz_curve = Geom_BezierCurve(poles)
    bz_curve_edge = BRepBuilderAPI_MakeEdge(bz_curve).Edge()
    bz_curve_wire = BRepBuilderAPI_MakeWire(bz_curve_edge).Wire()
    display.DisplayShape(bz_curve_wire)

    # profile
    origin = gp_Pnt(points[0][0], points[0][1], -1.0)
    direction = gp_Dir(0, 0, 1)
    vector = gp_Ax2(origin, direction)
    radius = 1.60
    circle = gp_Circ(vector, radius)
    circle_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    profile = BRepBuilderAPI_MakeWire(circle_edge).Wire()
    display.DisplayShape(profile)

    # pipe
    pipeBuilder = BRepOffsetAPI_MakePipeShell(bz_curve_wire)
    law_f = Law_Linear()
    law_f.Set(0, 0.5, 1, 1)
    pipeBuilder.SetLaw(profile, law_f, False, True)
    return pipeBuilder.Shape()


def generate_4(points):
    # ref: https://stackoverflow.com/questions/47163841/pythonocc-opencascade-create-pipe-along-straight-lines-through-points-profile
    # using the cylinders for the tube and spheres for the connections
    from OCC.Core.gp import gp_Pnt, gp_Circ, gp_Ax2, gp_Dir
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
    from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
    from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse

    # convert [x, y, z] to gp_Pnt(x, y, z)
    array = []
    for point in points:
        array.append(gp_Pnt(point[0], point[1], point[2]))
    array.append(gp_Pnt(points[-1][0], points[-1][1], -1.0))

    # generate cylinders
    radius = 1.60
    pipes = []
    for i in range(len(array) - 1):
        edge = BRepBuilderAPI_MakeEdge(array[i], array[i + 1]).Edge()
        makeWire = BRepBuilderAPI_MakeWire(edge)
        makeWire.Build()
        wire = makeWire.Wire()

        direction = gp_Dir(
            array[i + 1].X() - array[i].X(),
            array[i + 1].Y() - array[i].Y(),
            array[i + 1].Z() - array[i].Z()
        )
        circle = gp_Circ(gp_Ax2(array[i], direction), radius)
        profile_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
        profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()
        profile_face = BRepBuilderAPI_MakeFace(profile_wire).Face()
        pipes.append(BRepOffsetAPI_MakePipe(wire, profile_face).Shape())

    # fuse pipes with a sphere at each joining point
    pipe = pipes[0]
    for i in range(len(array) - 1):
        sphere = BRepPrimAPI_MakeSphere(array[i], radius).Shape()
        pipe = BRepAlgoAPI_Fuse(pipe, sphere).Shape()
        pipe = BRepAlgoAPI_Fuse(pipe, pipes[i]).Shape()

    return pipe


def generate_3(points):
    # ref: https://stackoverflow.com/questions/47163841/pythonocc-opencascade-create-pipe-along-straight-lines-through-points-profile
    # generate the pipe as sections and fillet the joins
    # fails because the gp_Pln is invalid on thef illet side
    from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Circ, gp_Pln, gp_Ax2
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
    from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe
    from OCC.Core.TColgp import TColgp_Array1OfPnt

    # the points
    length = len(points)
    poles = TColgp_Array1OfPnt(0, length)
    for i in range(length):
        point = gp_Pnt(points[i][0], points[i][1], points[i][2])
        poles.SetValue(i, point)
    print(poles.Length(), len(poles))

    # the edges
    edges = []
    for i in range(len(poles) - 1):
        edge = BRepBuilderAPI_MakeEdge(poles[i], poles[i + 1]).Edge()
        edges.append(edge)
        # display.DisplayShape(edge)

    # inbetween
    fillet_radius = 0.3
    fillets = []
    for i in range(len(poles) - 2):
        # if we send the referenced edges, they'll be nulled as the fillet algo continues
        p1 = poles[i]
        p2 = poles[i + 1]
        p3 = poles[i + 2]
        e1 = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
        e2 = BRepBuilderAPI_MakeEdge(p2, p3).Edge()
        fillet = filletEdges(e1, e2, fillet_radius, None)
        fillets.append(fillet)
        print(fillet)
        # display.DisplayShape(fillet)

    # the wire
    # makeWire = BRepBuilderAPI_MakeWire()
    # for i in range(len(edges)):
    #    makeWire.Add(edges[i])
    #    makeWire.Add(fillets[i])
#
    # makeWire.Build()
    # wire = makeWire.Wire()
    # the pipe
    # radius = 1.60
    # dir = gp_Dir(0, 1, 0)
    # circle = gp_Circ(gp_Ax2(points[0], dir), radius)
    # profile_edge = BRepBuilderAPI_MakeEdge(circle).Edge()
    # profile_wire = BRepBuilderAPI_MakeWire(profile_edge).Wire()
    # profile_face = BRepBuilderAPI_MakeFace(profile_wire).Face()
    # return BRepOffsetAPI_MakePipe(wire, profile_face).Shape()


def filletEdges(ed1, ed2, radius, plane):
    from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo
    from OCC.Core.gp import gp_Pln
    f = ChFi2d_AnaFilletAlgo()
    f.Init(ed1, ed2, gp_Pln())
    f.Perform(radius)
    result = f.Result(ed1, ed2)
    return result


if __name__ == "__main__":
    # pipe()

    points = [
        [12.734671415451, -4.014806351862397, 222.7628290443381],
        [13.117366356742401, -5.5331802141921, 218.01434661348654],
        [13.500061298034101, -7.051554076521899, 213.265864182635],
        [13.8827562393258, -8.569927938851599, 208.51738175178352],
        [14.265451180617502, -10.088301801181299, 203.7688993209319],
        [14.648146121909202, -11.606675663511098, 199.02041689008],
        [15.030841063200901, -13.125049525840797, 194.27193445922902],
        [15.413536004492602, -14.6434233881706, 189.523452028377],
        [15.796230945784302, -16.1617972505003, 184.774969597526],
        [16.178925887076, -17.68017111283, 180.026487166674],
    ]
    shp = generate_3(points)
    # display.DisplayShape(shp)

    display.FitAll()
    start_display()

    # 私も同じ結果になった。bz_curve_wireは正しい形状になっていますか？
    # I got the same result. bz_curve_wire is in the right shape?

    # あなたの generate_3の中のfilletEdgeがのnullを返している。
    # ChFi2d_AnaFilletAlgoは添付画像の緑と青のようなEdgeを要求しますが、あなたのコードではEdge同士に角度がありません。
    # このサンプルが参考になるのではないか？　https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_2d_fillet.py

    # The filletEdge in your generate_3 is returning null.
    # ChFi2d_AnaFilletAlgo requires Edges like the green and blue in the attached image, but in your code there is no angle between the Edges.
    # Maybe this sample would be helpful?　https://github.com/tpaviot/pythonocc-demos/blob/master/examples/core_2d_fillet.py