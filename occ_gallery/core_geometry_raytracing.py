# Copyright 2010-2017 Thomas Paviot (tpaviot@gmail.com)
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
import sys

from OCC.Display.SimpleGui import init_display
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeCone
from OCC.Core.Graphic3d import Graphic3d_NOM_PLASTIC, Graphic3d_NOM_ALUMINIUM
from OCC.Core.V3d import V3d_SpotLight, V3d_XnegYnegZpos
from OCC.Core.Quantity import (
    Quantity_Color,
    Quantity_NOC_WHITE,
    Quantity_NOC_CORAL2,
    Quantity_NOC_BROWN,
)
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Vec, gp_Pnt, gp_Dir, gp_Ax3, gp_Lin

from OCC.Extend.ShapeFactory import translate_shp
from OCC.Extend.DataExchange import read_step_file

from OCC.Core.BRepTools import breptools
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRep import BRep_Builder

# then inits display
display, start_display, add_menu, add_function_to_menu = init_display()

cylinder_head = TopoDS_Shape()
builder = BRep_Builder()
breptools.Read(cylinder_head, "../assets/models/cylinder_head.brep", builder)

beam = gp_Ax3(gp_Pnt(10, 0, 0), gp_Dir(1, 1, 1))

from OCC.Core.BRepIntCurveSurface import BRepIntCurveSurface_Inter
lin = gp_Lin(beam.Location(), beam.Direction())
api = BRepIntCurveSurface_Inter()
api.Init(cylinder_head, lin, 1.0E-9)
dat = []
while api.More():
    p = api.Point()
    p.Dump()
    data = [p.W(), p.U(), p.V(), p.Pnt(), api.Face(), p.Transition()]
    dat.append(data)
    api.Next()

dat.sort(key=lambda e: e[0])
[display.DisplayShape(d[3]) for d in dat]
display.DisplayShape(beam.Location())
display.DisplayShape(cylinder_head)

display.FitAll()
start_display()
