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

from OCC.Core.gp import gp_Pnt, gp_Pln, gp_Vec, gp_Ax3, gp_Dir
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_CompSolid
from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepFilletAPI import BRepFilletAPI_MakeFillet
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeShapeOnMesh, BRepBuilderAPI_MakeSolid
from OCC.Core.ChFi2d import ChFi2d_AnaFilletAlgo, ChFi2d_ChamferAPI
from OCC.Core.ChFi3d import ChFi3d_Builder, ChFi3d_FilBuilder, ChFi3d_ChBuilder, ChFi3d_FilletShape
from OCC.Core.ChFiDS import ChFiDS_ChamfMethod
# from OCC.Core.ChFiKPart import ChFiDS_TypeOfConcavity
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCCUtils.Construct import make_plane, make_edge

from OCC.Extend.ShapeFactory import make_wire

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_functionto_menu = init_display()

# Defining the points
p1 = gp_Pnt(0, 0, 0)
p2 = gp_Pnt(5, 5, 0)
p3 = gp_Pnt(-5, 5, 0)

ax32 = gp_Ax3(p3, gp_Dir(gp_Vec(p3, p2).XYZ()))
ax21 = gp_Ax3(p3, gp_Dir(gp_Vec(p2, p1).XYZ()))

# Making the edges
ed1 = BRepBuilderAPI_MakeEdge(p3, p2).Edge()
ed2 = BRepBuilderAPI_MakeEdge(p2, p1).Edge()

# Making the 2dFillet
f2 = ChFi2d_AnaFilletAlgo()
f2.Init(ed1, ed2, gp_Pln())
f2.Perform(1.0)  # radius
fillet2d = f2.Result(ed1, ed2)

pln1 = make_plane(gp_Pnt(0, 0, 0), gp_Vec(0, 0, 1),
                  0, 10, 0, 10)
pln2 = make_plane(gp_Pnt(0, 0, 0), gp_Vec(0, -1, -1),
                  -10, 0, -10, 0)
edge = make_edge(gp_Pnt(0, 0, 0), gp_Pnt(10, 0, 0))

fused_shape = BRepAlgoAPI_Fuse(pln1, pln2).Shape()
sew = BRepBuilderAPI_Sewing()
sew.Add(pln1)
sew.Add(pln2)
sew.Perform()
fused_shape = sew.SewedShape()

builder = BRep_Builder()
comp = TopoDS_Compound()
builder.MakeCompound(comp)
builder.Add(comp, pln1)
builder.Add(comp, pln2)
builder.Add(comp, edge)

fused_shape = BRepBuilderAPI_MakeSolid(comp).Solid()

f3 = ChFi3d_FilBuilder(fused_shape)
f3.Add(1, edge)
f3.Compute()
# RuntimeError: Standard_FailureThere are no suitable edges for chamfer or fillet raised from method Compute of class ChFi3d_Builder


# f3 = BRepFilletAPI_MakeFillet(fused_shape)
# f3.Add(1, edge)
# f3.Build()
# RuntimeError: Standard_FailureThere are no suitable edges for chamfer or fillet raised from method Build of class BRepBuilderAPI_MakeShape
# print(f3.BadShape())
print(fused_shape)
print(f3.IsDone())
print(f3.HasResult())

# Create and display a wire
w = make_wire([ed1, fillet2d, ed2])
# display.DisplayShape(w)
display.DisplayShape(ed1, color="BLUE1")
display.DisplayShape(fillet2d)
display.DisplayShape(ed2, color="BLUE1")

display.DisplayShape(fused_shape)
display.DisplayShape(edge)
# display.DisplayShape(pln1)
# display.DisplayShape(pln2)
# display.DisplayShape(f3.Shape())
display.FitAll()
start_display()
