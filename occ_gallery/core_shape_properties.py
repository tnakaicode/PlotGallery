#!/usr/bin/env python

# Copyright 2009-2016 Thomas Paviot (tpaviot@gmail.com)
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

from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Dir
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop

from OCC.Extend.TopologyUtils import TopologyExplorer


def cube_inertia_properties():
    """Compute the inertia properties of a shape"""
    # Create and display cube
    print("Creating a cubic box shape (50*50*50)")
    cube_shape = BRepPrimAPI_MakeBox(gp_Ax2(gp_Pnt(0,0,0), gp_Dir(0,0.5,1)), 50.0, 50.0, 50.0).Shape()
    # Compute inertia properties
    props = GProp_GProps()
    brepgprop.VolumeProperties(cube_shape, props)
    # Get inertia properties
    mass = props.Mass()
    cog = props.CentreOfMass()
    matrix_of_inertia = props.MatrixOfInertia()
    # Display inertia properties
    print("Cube mass = %s" % mass)
    cog_x, cog_y, cog_z = cog.Coord()
    print("Center of mass: x = %f;y = %f;z = %f;" % (cog_x, cog_y, cog_z))
    print("Matrix of inertia", matrix_of_inertia.Value(1,1), matrix_of_inertia.Value(1,2), matrix_of_inertia.Value(1,3))
    print("                 ", matrix_of_inertia.Value(2,1), matrix_of_inertia.Value(2,2), matrix_of_inertia.Value(2,3))
    print("                 ", matrix_of_inertia.Value(3,1), matrix_of_inertia.Value(3,2), matrix_of_inertia.Value(3,3))


def shape_faces_surface():
    """Compute the surface of each face of a shape"""
    # first create the shape
    the_shape = BRepPrimAPI_MakeBox(50.0, 30.0, 10.0).Shape()
    # then loop over faces
    t = TopologyExplorer(the_shape)
    props = GProp_GProps()
    shp_idx = 1
    for face in t.faces():
        brepgprop.SurfaceProperties(face, props)
        face_surf = props.Mass()
        print("Surface for face nbr %i : %f" % (shp_idx, face_surf))
        shp_idx += 1


if __name__ == "__main__":
    cube_inertia_properties()
    shape_faces_surface()
