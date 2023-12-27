#!/usr/bin/env python

# Copyright 2017 Thomas Paviot (tpaviot@gmail.com)
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

from OCC.Core.gp import gp_Pnt
from OCC.Core.Bnd import Bnd_Box
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh

from OCC.Extend.ShapeFactory import get_aligned_boundingbox


def get_boundingbox(shape, tol=1e-6, use_mesh=True):
    """return the bounding box of the TopoDS_Shape `shape`
    Parameters
    ----------
    shape : TopoDS_Shape or a subclass such as TopoDS_Face
        the shape to compute the bounding box from
    tol: float
        tolerance of the computed boundingbox
    use_mesh : bool
        a flag that tells whether or not the shape has first to be meshed before the bbox
        computation. This produces more accurate results
    """
    bbox = Bnd_Box()
    bbox.SetGap(tol)
    if use_mesh:
        mesh = BRepMesh_IncrementalMesh()
        mesh.SetParallelDefault(True)
        mesh.SetShape(shape)
        mesh.Perform()
        if not mesh.IsDone():
            raise AssertionError("Mesh not done.")
    brepbndlib.Add(shape, bbox, use_mesh)

    xmin, ymin, zmin, xmax, ymax, zmax = bbox.Get()
    bbox_shape = BRepPrimAPI_MakeBox(gp_Pnt(xmin, ymin, zmin),
                                     gp_Pnt(xmax, ymax, zmax)).Shape()
    return bbox, bbox_shape


from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

print("Box bounding box computation")
box_shape = BRepPrimAPI_MakeBox(10.0, 20.0, 30.0).Shape()
bb1, box1 = get_boundingbox(box_shape)
display.DisplayShape(box_shape)
display.DisplayShape(box1, transparency=0.9)
print(bb1.Get())

print("Cylinder bounding box computation")
cyl_shape = BRepPrimAPI_MakeCylinder(10.0, 20.0).Shape()
bb2, box2 = get_boundingbox(cyl_shape)
display.DisplayShape(cyl_shape)
display.DisplayShape(box2, transparency=0.9)
print(bb2.Get())

print("Torus bounding box computation")
torus_shape = BRepPrimAPI_MakeCylinder(15.0, 5.0).Shape()
bb3, box3 = get_boundingbox(torus_shape)
display.DisplayShape(torus_shape)
display.DisplayShape(box3, transparency=0.9)
print(bb3.Get())

display.FitAll()
start_display()
