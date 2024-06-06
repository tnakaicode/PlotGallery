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

from OCCUtils.Construct import make_polygon, make_wire, make_vertex, make_edge, dir_to_vec
from OCCUtils.Common import minimum_distance

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

shp = read_step_file("../assets/models/face_recognition_sample_part.stp"
                     # os.path.join("..", "assets", "models", "face_recognition_sample_part.stp")
                     )
display.DisplayShape(shp, transparency=0.9)

pts = [
    gp_Pnt(-1, -1, 0),
    gp_Pnt(10, 10, 0),
    gp_Pnt(10, 10, 20),
    # gp_Pnt(30, 40, 1),
]
wire = make_polygon(pts, closed=True)
axis = gp_Ax3(gp_Pnt(200, -150, 100), gp_Dir(0.9, 1, 0))
vert = make_vertex(axis.Location())
trsf = gp_Trsf()
trsf.SetTransformation(axis)
wire.Move(TopLoc_Location(trsf.Inverted()))
display.DisplayShape(wire)
display.DisplayShape(axis.Location())
print(axis.Location())

lin = gp_Lin(axis.Location(), gp_Dir(0, 1, 0))


from OCC.Core.BRepIntCurveSurface import BRepIntCurveSurface_Inter
from OCC.Core.BRepProj import BRepProj_Projection
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
api = BRepIntCurveSurface_Inter()
api.Init(shp, lin, 1.0E-9)
shp_int = []
while api.More():
    dst = api.Pnt().Distance(axis.Location())
    print(api.W(), api.Pnt())

    proj = BRepProj_Projection(wire, api.Face(), lin.Direction())
    proj_list = []
    while proj.More():
        poly = proj.Current()
        proj_list.append([
            minimum_distance(vert, poly)[0] - dst,
            poly,
        ])
        proj.Next()
    proj_list.sort(key=lambda e: np.abs(e[0]))
    poly = proj_list[0][1]

    face_trim = BRepAlgo_FaceRestrictor()
    face_trim.Init(api.Face(), True, True)
    face_trim.Add(poly)
    face_trim.Perform()
    while face_trim.More():
        face = face_trim.Current()
        face_trim.Next()

    shp_int.append([api.W(),  # 0
                    api.U(),  # 1
                    api.V(),  # 2
                    api.Pnt(),  # 3
                    api.Face(),  # 4
                    poly,  # 5
                    face,  # 6
                    api.Transition(),  # 7
                    ])

    display.DisplayShape(poly, color="BLUE1")
    display.DisplayShape(face, color="BLUE1")

    api.Next()
shp_int.sort(key=lambda e: e[0])


from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
api = BRepOffsetAPI_ThruSections()
api.SetSmoothing(False)
api.AddWire(shp_int[0][5])
api.AddWire(shp_int[1][5])
api.Build()
display.DisplayShape(api.Shape())


from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeShell, BRepBuilderAPI_MakeSolid
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
# shell1 = BRepBuilderAPI_MakeShell(BRepAdaptor_Surface(shp_int[2][6], True).Surface()).Shell()
# shell2 = BRepBuilderAPI_MakeShell(BRepAdaptor_Surface(shp_int[3][6], True)).Shell()
# solid = BRepBuilderAPI_MakeSolid(shell1, shell2).Solid()
# display.DisplayShape(solid)

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
