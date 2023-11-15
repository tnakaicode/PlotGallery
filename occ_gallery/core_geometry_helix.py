#!/usr/bin/env python
# coding: utf-8

from OCC.Display.SimpleGui import init_display

import numpy as np
from math import pi

from OCC.Core.gp import gp_Pnt2d, gp_Pnt, gp_Lin2d, gp_Ax3, gp_Dir2d, gp_Dir
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_CylindricalSurface, Geom_ToroidalSurface, Geom_Curve, Geom_Surface, Geom_ConicalSurface
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCCUtils.Common import vertex2pnt
from OCCUtils.Construct import make_face, make_edge, make_wire

display, start_display, add_menu, add_function_to_menu = init_display()


def make_helix_wire(segment=Geom_Curve, surface=Geom_Surface, t0=0, t1=1):
    print(segment, surface)
    helix_api = BRepBuilderAPI_MakeEdge(aSegment, surface, t0, t1)
    helix_edge = helix_api.Edge()
    helix_vert = [vertex2pnt(helix_api.Vertex1()),
                  vertex2pnt(helix_api.Vertex2())]
    print(helix_vert)
    print(segment.Value(t0).X(), segment.Value(t0).Y())
    print(segment.Value(t1).X(), segment.Value(t1).Y())
    print(surface.Value(segment.Value(t0).X(), segment.Value(t0).Y()))
    print(surface.Value(segment.Value(t1).X(), segment.Value(t1).Y()))
    if helix_vert[0].IsEqual(helix_vert[1], 0.1):
        helix_wire = make_wire(helix_edge)
    else:
        helix_wire = make_wire([helix_edge, make_edge(*helix_vert)])
    return helix_wire


aCylinder = Geom_CylindricalSurface(gp_Ax3(), 3.0)
aCone = Geom_ConicalSurface(gp_Ax3(gp_Pnt(15, 0, 0), gp_Dir(0, 0, 1)),
                            np.deg2rad(30), 3)
aTorus = Geom_ToroidalSurface(gp_Ax3(gp_Pnt(40, 0, 0), gp_Dir(0, 0, 1)),
                              10, 3)

# Build an helix
u0, v0 = pi, 1.0
ur, vr = 1.2, 1.0
ut, vt = 1 / ur, 1 / vr
uv = np.sqrt(ut**2 + vt**2)
aLine2d = gp_Lin2d(gp_Pnt2d(u0, v0), gp_Dir2d(ut, vt))
aSegment = GCE2d_MakeSegment(aLine2d, 0, 1).Value()

# Cylinder
t0, t1 = 0.0, uv * 2 * pi * ur
helix_wire = make_helix_wire(aSegment, aCylinder, t0, t1)
face = make_face(aCylinder.Cylinder(), helix_wire)
display.DisplayShape(make_face(aCylinder.Cylinder(), 0, 2 * pi, 0, 10))
display.DisplayShape(helix_wire)
# display.DisplayShape(face)

# Cone
t0, t1 = 0.0, uv * 2 * pi * ur
helix_wire = make_helix_wire(aSegment, aCone, t0, t1)
face = make_face(aCone.Cone(), helix_wire)
display.DisplayShape(make_face(aCone.Cone(), 0, 2 * pi, 0, 10))
display.DisplayShape(helix_wire)
# display.DisplayShape(face)

# Torus
t0, t1 = 0.0, 1.5 * uv * 2 * pi * ur
helix_wire = make_helix_wire(aSegment, aTorus, t0, t1)
face = make_face(aTorus.Torus(), helix_wire)
display.DisplayShape(make_face(aTorus.Torus(), 0, 2 * pi, 0, 2 * pi))
display.DisplayShape(helix_wire)
# display.DisplayShape(face)

display.DisplayShape(aSegment)
display.FitAll()
start_display()

# The general method to directly create an edge is to give.
#
# - a 3D curve C as the support (geometric domain) of the edge,
# - two vertices V1 and V2 to limit the curve (definition of the restriction of the edge), and
# - two real values p1 and p2 which are the parameters for the vertices V1 and V2 on the curve.
#   The curve may be defined as a 2d curve in the parametric space of a surface: a pcurve.
#   The surface on which the edge is built is then kept at the level of the edge.
#   The default tolerance will be associated with this edge. Rules applied to the arguments: For the curve:
# - The curve must not be a 'null handle'.
# - If the curve is a trimmed curve the basis curve is used. For the vertices:
# - Vertices may be null shapes.
#   When V1 or V2 is null the edge is open in the corresponding direction and
#   the parameter value p1 or p2 must be infinite (remember that Precision::Infinite() defines an infinite value).
# - The two vertices must be identical if they have the same 3D location.
#   Identical vertices are used in particular when the curve is closed. For the parameters:
# - The parameters must be in the parametric range of the curve (or the basis curve if the curve is trimmed).
#   If this condition is not satisfied the edge is not built, and the Error function will return BRepAPI_ParameterOutOfRange.
# - Parameter values must not be equal.
#   If this condition is not satisfied (i.e. if | p1 - p2 | ) the edge is not built,
#   and the Error function will return BRepAPI_LineThroughIdenticPoints.
#   Parameter values are expected to be given in increasing order: C->FirstParameter()
# - If the parameter values are given in decreasing order the vertices are switched,
#   i.e. the "first vertex" is on the point of parameter p2 and the "second vertex" is on the point of parameter p1.
#   In such a case, to keep the original intent of the construction, the edge will be oriented "reversed".
# - On a periodic curve the parameter values p1 and p2 are adjusted by adding or subtracting the period to obtain p1 in the parametric range of the curve,
#   and p2] such that [ p1 , where Period is the period of the curve.
# - A parameter value may be infinite.
#   The edge is open in the corresponding direction.
#   However the corresponding vertex must be a null shape.
#   If this condition is not satisfied the edge is not built,
#   and the Error function will return BRepAPI_PointWithInfiniteParameter.
# - The distance between the vertex and the point evaluated on the curve with the parameter,
#   must be lower than the precision of the vertex.
#   If this condition is not satisfied the edge is not built,
#   and the Error function will return BRepAPI_DifferentsPointAndParameter. Other edge constructions
# - The parameter values can be omitted, they will be computed by projecting the vertices on the curve.
#   Note that projection is the only way to evaluate the parameter values of the vertices on the curve:
#   vertices must be given on the curve,
#   i.e. the distance from a vertex to the curve must be less than or equal to the precision of the vertex.
#   If this condition is not satisfied the edge is not built,
#   and the Error function will return BRepAPI_PointProjectionFailed.
# - 3D points can be given in place of vertices.
#   Vertices will be created from the points (with the default topological precision Precision::Confusion()). Note:
# - Giving vertices is useful when creating a connected edge.
# - If the parameter values correspond to the extremities of a closed curve, points must be identical, or at least coincident.
#   If this condition is not satisfied the edge is not built,
#   and the Error function will return BRepAPI_DifferentPointsOnClosedCurve.
# - The vertices or points can be omitted if the parameter values are given.
#   The points will be computed from the parameters on the curve.
#   The vertices or points and the parameter values can be omitted.
#   The first and last parameters of the curve will then be used.
# Auxiliary methods
#
