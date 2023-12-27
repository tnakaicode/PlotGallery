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
from OCC.Core.TopAbs import TopAbs_ON
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Cut
from OCC.Core.gp import gp_Vec, gp_Pnt, gp_Dir, gp_Ax3, gp_Lin

from OCC.Extend.ShapeFactory import translate_shp, make_edge
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.DataExchange import read_step_file
from OCCUtils.Common import point_in_solid, point_in_boundingbox

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
from OCC.Core.Geom import Geom_Line
lin = gp_Lin(beam.Location(), beam.Direction())
api = BRepIntCurveSurface_Inter()
api.Init(cylinder_head, lin, 1.0E-9)
dat = []
while api.More():
    p = api.Point()
    p.Dump()
    # 0: W, 1: U, 2: V
    # 3: gp_Pnt, 4: TopoDS_Face
    # 5: Transition
    # 6: TopAbs_ON(2)/TopAbs_OUT(1)/TopAbs_IN(0)
    data = [p.W(), p.U(), p.V(), p.Pnt(), api.Face(), p.Transition(), point_in_solid(cylinder_head, api.Pnt())]
    dat.append(data)
    api.Next()

from OCC.Core.BRepGProp import BRepGProp_Face, BRepGProp_Vinert
from OCC.Core.TColStd import TColStd_Array1OfReal

array = TColStd_Array1OfReal(1, 100)
prop_face = BRepGProp_Face(dat[0][4])
prop_face.UKnots(array)
for i in [1, 2, 10, 20]:
    print(array.Value(i))

dat.sort(key=lambda e: e[0])
for i, d in enumerate(dat):
    if i == 0:
        pass
    else:
        v = (dat[i][0] + dat[i-1][0])/2
        val, _ = point_in_solid(cylinder_head, Geom_Line(lin).Value(v))
        if val == True: # IN
            display.DisplayShape(make_edge(dat[i-1][3], dat[i][3]))
    
    display.DisplayShape(d[3])
display.DisplayShape(beam.Location())
display.DisplayShape(cylinder_head, transparency=0.2)

display.FitAll()
start_display()
