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

import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Circ, gp_ZOX, gp_Vec, gp_Pln
from OCC.Core.Geom import Geom_BezierCurve
from OCC.Core.GeomAbs import GeomAbs_Plane
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TopoDS import TopoDS_Shape, TopoDS_Face, topods
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCone
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_MakePipe


from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


def generate_curved_channel(cylinder_offset: float = 5, diameter: float = 3.0) -> TopoDS_Shape:
    '''
    Generates a TopoDS_Shape from the Needle Channel's points
    Cylinder Offset is for height offset
    diameter is the channel's diameter
    '''
    # offset points using z axis and cylinder's offset
    # and convert into a gp_Pnt

    data = [
        [-33.708023525841, -2.496432489532598, 206.2113114751896],
        [-33.325328584549, -4.014806351862397, 201.4628290443381],
        [-32.9426336432576, -5.5331802141921, 196.71434661348653],
        [-32.559938701965905, -7.051554076521899, 191.965864182635],
        [-32.1772437606742, -8.569927938851599, 187.2173817517835],
        [-31.7945488193825, -10.088301801181299, 182.46889932093188],
        [-31.411853878090803, -11.606675663511098, 177.72041689008],
        [-31.0291589367991, -13.125049525840797, 172.971934459229],
        [-30.6464639955074, -14.6434233881706, 168.22345202837698],
        [-30.2637690542157, -16.1617972505003, 163.47496959752598],
        [-29.881074112924, -17.68017111283, 158.726487166674]
    ]

    points = []
    for point in data:
        points.append(gp_Pnt(point[0], point[1], point[2] - cylinder_offset))

    radius = diameter / 2

    # generate starting point on top (cone)
    p1 = points[0]
    p2 = points[1]
    v12 = gp_Vec(p1, p2)
    vector = np.array([v12.X(), v12.Y(), v12.Z()])
    length = np.linalg.norm(vector)
    direction = gp_Dir(v12)
    axis = gp_Ax2(p1, direction)
    pipe = BRepPrimAPI_MakeCone(axis, 0.0, radius, length).Shape()
    face = get_lowest_face(pipe)

    # for each (after the first), create a sphere and cylinder to next point to join
    for i in range(1, len(points) - 1):
        p1 = points[i]
        p2 = points[i + 1]

        edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()
        makeWire = BRepBuilderAPI_MakeWire(edge)
        makeWire.Build()
        wire = makeWire.Wire()
        cylinder = BRepOffsetAPI_MakePipe(wire, face).Shape()
        pipe = BRepAlgoAPI_Fuse(pipe, cylinder).Shape()
        face = get_lowest_face(cylinder)

    # add a curved pipe downwards using offset length and direction of last two points
    vector = get_vector(points[-2], points[-1], length)
    p1 = points[-1]
    p2 = gp_Pnt(p1.X() + vector.X(), p1.Y() + vector.Y(), p1.Z() + vector.Z())
    p3 = gp_Pnt(p2.X(), p2.Y(), p2.Z() - length)

    # curve joining two straight paths
    array = TColgp_Array1OfPnt(1, 3)
    array.SetValue(1, p1)
    array.SetValue(2, p2)
    array.SetValue(3, p3)
    bz_curve = Geom_BezierCurve(array)
    bend_edge = BRepBuilderAPI_MakeEdge(bz_curve).Edge()

    # assembling the path
    wire = BRepBuilderAPI_MakeWire(bend_edge).Wire()

    # shape using last face
    pipe_bend = BRepOffsetAPI_MakePipe(wire, face).Shape()
    pipe = BRepAlgoAPI_Fuse(pipe, pipe_bend).Shape()

    # add a cylinder from pipe to past bottom of cylinder
    base_point = gp_Pnt(p3.X(), p3.Y(), -0.01)
    face = get_lowest_face(pipe_bend)
    edge = BRepBuilderAPI_MakeEdge(p3, base_point).Edge()
    makeWire = BRepBuilderAPI_MakeWire(edge)
    makeWire.Build()
    wire = makeWire.Wire()
    cylinder = BRepOffsetAPI_MakePipe(wire, face).Shape()
    pipe = BRepAlgoAPI_Fuse(pipe, cylinder).Shape()

    return pipe


def face_is_plane(face: TopoDS_Face) -> bool:
    """
    Returns True if the TopoDS_Face is a plane, False otherwise
    """
    surf = BRepAdaptor_Surface(face, True)
    surf_type = surf.GetType()
    return surf_type == GeomAbs_Plane


def geom_plane_from_face(face: TopoDS_Face) -> gp_Pln:
    """
    Returns the geometric plane entity from a planar surface
    """
    return BRepAdaptor_Surface(face, True).Plane()


def get_faces(shape: TopoDS_Shape) -> list[TopoDS_Face]:
    '''
    returns a list of planar faces for the shape from highest to lowest
    '''
    def sortByZ(elem):
        return elem[1]

    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    faces = []
    while explorer.More():
        face = topods.Face(explorer.Current())
        if face_is_plane(face):
            a_plane = geom_plane_from_face(face)
            # face with it's z height
            faces.append([face, a_plane.Location().Z()])
        explorer.Next()
    faces.sort(key=sortByZ)
    return faces


def get_highest_face(shape: TopoDS_Shape) -> TopoDS_Face:
    faces = get_faces(shape)
    return faces[-1][0]


def get_lowest_face(shape: TopoDS_Shape) -> TopoDS_Face:
    faces = get_faces(shape)
    return faces[0][0]


def get_vector(p1: gp_Pnt, p2: gp_Pnt, length: float = 1.0) -> gp_Vec:
    vector = gp_Vec(
        p2.X() - p1.X(),
        p2.Y() - p1.Y(),
        p2.Z() - p1.Z())
    return vector.Normalized() * length


def get_direction(p1: gp_Pnt, p2: gp_Pnt) -> gp_Dir:
    vector = get_vector(p1, p2)
    return gp_Dir(vector.X(), vector.Y(), vector.Z())


if __name__ == "__main__":
    shp = generate_curved_channel()

    display.DisplayShape(shp)
    display.FitAll()
    start_display()
