#!/usr/bin/env python
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

import numpy as np
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.AIS import AIS_ColorScale, AIS_Axis, AIS_Triangulation
from OCC.Core.Graphic3d import Graphic3d_ZLayerId_TopOSD, Graphic3d_TMF_2d
from OCC.Core.gp import gp_XY, gp_Pnt, gp_Dir, gp_Ax1
from OCC.Core.Geom import Geom_Line
from OCC.Core.Poly import Poly_ListOfTriangulation, Poly_Triangulation, Poly_Triangle, Poly_Array1OfTriangle
from OCC.Core.TColgp import TColgp_Array1OfPnt

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

myBox = BRepPrimAPI_MakeBox(60, 60, 50).Shape()

line = Geom_Line(gp_Ax1(gp_Pnt(-100, 0, 0), gp_Dir()))
axis = AIS_Axis(gp_Ax1())

tam = [1 * np.pi, 1 * np.pi, 1 * np.pi]
spacing = [0.1, 0.1, 0.1]
hole_size = [-0.3, 0.3]

tx, ty, tz = tam
sx, sy, sz = spacing
neg, pos = hole_size

px = np.linspace(-tx / 2, tx / 2, int(tx / sx) + 1)
py = np.linspace(-ty / 2, ty / 2, int(ty / sy) + 1)
pz = np.linspace(-tz / 2, tz / 2, int(tz / sz) + 1)
x, y, z = np.meshgrid(px, py, pz)
f = np.cos(x) + np.cos(y) + np.cos(z)
m = np.array(((f > neg) & (f < pos)) * 1.0)

from skimage import measure
verts, faces, norm, val = measure.marching_cubes(m, level=None)
#pts = TColgp_Array1OfPnt(1, verts.shape[0])
#tri = Poly_Array1OfTriangle(1, faces.shape[0])

print(verts.shape[0], faces.shape[0])
poly = Poly_Triangulation(verts.shape[0], faces.shape[0], False)
for i, xyz in enumerate(verts):
    poly.SetNode(i + 1, gp_Pnt(float(xyz[0]), float(xyz[1]), float(xyz[2])))
for i, ixyz in enumerate(faces):
    poly.SetTriangle(i + 1, Poly_Triangle(int(ixyz[0]), int(ixyz[1]), int(ixyz[2])))
print(poly.NbNodes(), poly.NbTriangles())
print(poly.UnloadDeferredData())
ais_poly = AIS_Triangulation(poly)

display.Context.Display(ais_poly, True)
# display.DisplayShape(poly)
start_display()
