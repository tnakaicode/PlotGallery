# https://github.com/tpaviot/pythonocc-core/issues/1326
from __future__ import print_function

import os
import os.path
import sys
import numpy as np

from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Ax3, gp_Trsf
from OCC.Core.gp import gp_Lin
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.DataExchange import read_step_file

from OCCUtils.Construct import make_polygon, make_wire, make_vertex, make_edge
from OCCUtils.Common import minimum_distance

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

shp = read_step_file("../assets/models/face_recognition_sample_part.stp"
                     # os.path.join("..", "assets", "models", "face_recognition_sample_part.stp")
                     )
display.DisplayShape(shp)

pts = [
    gp_Pnt(-1, -1, 0),
    gp_Pnt(10, 10, 0),
    gp_Pnt(10, 10, 20),
    # gp_Pnt(30, 40, 1),
]
wire = make_polygon(pts, closed=True)
axis = gp_Ax3(gp_Pnt(200, -150, 100), gp_Dir(0.9, 1, 0))
trsf = gp_Trsf()
trsf.SetTransformation(axis)
wire.Move(TopLoc_Location(trsf.Inverted()))
display.DisplayShape(wire)
display.DisplayShape(axis.Location())
print(axis.Location())


from OCC.Core.BRepProj import BRepProj_Projection
proj = BRepProj_Projection(wire, shp, gp_Dir(0, 1, 0))
list_wire = []
while proj.More():
    poly = proj.Current()
    list_wire.append(
        [minimum_distance(make_vertex(axis.Location()), poly)[0], poly])
    proj.Next()
    display.DisplayShape(poly, color="BLUE1")
list_wire.sort(key=lambda e: e[0])


from OCC.Core.BRepIntCurveSurface import BRepIntCurveSurface_Inter
lin = gp_Lin(axis.Location(), gp_Dir(0, 1, 0))
api = BRepIntCurveSurface_Inter()
api.Init(shp, lin, 1.0E-9)
shp_int = []
while api.More():
    print(api.W())
    shp_int.append([api.W(), api.U(), api.V(), api.Pnt(),
                   api.Face(), api.Transition()])
    api.Next()
shp_int.sort(key=lambda e: e[0])

# for i, p in enumerate(shp_int):
#    print(p, list_wire[i])
#    display.DisplayShape(p[3])
#
#
# from OCC.Core.Geom import Geom_Line
# glin = Geom_Line(lin)
# for i, p1 in enumerate(shp_int[1:]):
#    p0 = shp_int[i]
#    p = glin.Value((p0[0] + p1[0]) / 2)
#

display.FitAll()
start_display()
