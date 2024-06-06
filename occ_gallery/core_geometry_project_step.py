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
from OCC.Extend.DataExchange import read_step_file, write_step_file

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
api_int = BRepIntCurveSurface_Inter()
api_int.Init(shp, lin, 1.0E-9)
shp_int = []
while api_int.More():
    dst = api_int.Pnt().Distance(axis.Location())
    print(api_int.W(), api_int.Pnt())

    proj = BRepProj_Projection(wire, api_int.Face(), lin.Direction())
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
    face_trim.Init(api_int.Face(), True, True)
    face_trim.Add(poly)
    face_trim.Perform()
    while face_trim.More():
        face = face_trim.Current()
        face_trim.Next()

    shp_int.append([api_int.W(),  # 0
                    api_int.U(),  # 1
                    api_int.V(),  # 2
                    api_int.Pnt(),  # 3
                    api_int.Face(),  # 4
                    poly,  # 5
                    face,  # 6
                    api_int.Transition(),  # 7
                    ])

    display.DisplayShape(poly, color="BLUE1")
    display.DisplayShape(face, color="BLUE1")

    api_int.Next()
shp_int.sort(key=lambda e: e[0])


from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
api_thru = BRepOffsetAPI_ThruSections()
api_thru.SetSmoothing(False)
api_thru.AddWire(shp_int[0][5])
api_thru.AddWire(shp_int[1][5])
api_thru.Build()
# display.DisplayShape(api.Shape())


from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_SOLID
splitter = BOPAlgo_Splitter()
splitter.AddArgument(shp)
splitter.AddTool(api_thru.Shape())
splitter.AddTool(shp_int[0][5])
splitter.AddTool(shp_int[1][5])
splitter.Perform()
print(splitter.Arguments())
print(splitter.ShapesSD())
exp = TopExp_Explorer(splitter.Shape(), TopAbs_SOLID)
i = 0
while exp.More():
    display.DisplayShape(exp.Current(), transparency=0.6)
    write_step_file(exp.Current(), f"split_{i:03d}.stp")
    exp.Next()
    i += 1

display.FitAll()
start_display()
