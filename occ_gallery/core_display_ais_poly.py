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
#from OCC.Core.Graphic3d import Graphic3d_ZLayerId_TopOSD, Graphic3d_TMF_2d
from OCC.Core.gp import gp_XY, gp_Pnt, gp_Dir, gp_Ax1
from OCC.Core.Geom import Geom_Line
from OCC.Core.Poly import Poly_ListOfTriangulation, Poly_Triangulation, Poly_Triangle, Poly_Array1OfTriangle
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRep import BRep_Tool, BRep_Builder
from OCC.Core.gp import gp_Pnt
from OCC.Core.TopoDS import TopoDS_Compound
from OCCUtils.Construct import make_polygon, make_face

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

tam = [2 * np.pi, 2 * np.pi, 2 * np.pi]
spacing = [0.25, 0.25, 0.25]
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

print(verts.shape[0], faces.shape[0])
poly = Poly_Triangulation(verts.shape[0], faces.shape[0], False)
poly_dat = verts[faces]
for i, xyz in enumerate(verts):
    poly.SetNode(i + 1, gp_Pnt(float(xyz[0]), float(xyz[1]), float(xyz[2])))
for i, ixyz in enumerate(faces):
    poly.SetTriangle(i + 1, Poly_Triangle(int(ixyz[0]), int(ixyz[1]), int(ixyz[2])))
print(poly.NbNodes(), poly.NbTriangles())
print(poly.UnloadDeferredData())
ais_poly = AIS_Triangulation(poly)

bild1 = BRep_Builder()
comp1 = TopoDS_Compound()
bild1.MakeCompound(comp1)
for i, dat in enumerate(poly_dat):
    p0 = gp_Pnt(float(dat[0, 0]), float(dat[0, 1]), float(dat[0, 2]))
    p1 = gp_Pnt(float(dat[1, 0]), float(dat[1, 1]), float(dat[1, 2]))
    p2 = gp_Pnt(float(dat[2, 0]), float(dat[2, 1]), float(dat[2, 2]))
    poly = make_polygon([p0, p1, p2], closed=True)
    face = make_face(poly, True)
    # bild1.Add(comp1, poly)
    bild1.Add(comp1, face)

display.Context.Display(ais_poly, True)
display.DisplayShape(comp1)
display.FitAll()
start_display()

"""
Triply Peridic Minimal Surface (TPMS)を生成する方法はないでしょうか？

GyroidはTPMSの一種です。
私のコードはmarching cubeによって、三角形要素で表現しているため、平面の集まりになっているだけで曲面ではありません。
また、Node数が増えるとファイルサイズが膨大になります。
B-Splineのように、曲面として形状を生成する方法を探しています。

How to generate Triply Peridic Minimal Surface (TPMS)?

Gyroid is a type of TPMS. 
My code is represented by a triangular element by means of a marching cube, which is just a collection of planes and not a curved surface. 
Also, the file size becomes huge when the number of Nodes increases. 
I am looking for a way to generate shapes as curved surfaces, like B-Spline. 

"""
