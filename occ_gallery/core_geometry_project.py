# https://github.com/tpaviot/pythonocc-core/issues/1326
from __future__ import print_function

import os
import os.path
import sys
import numpy as np

from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.TopTools import TopTools_ListIteratorOfListOfShape
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.BRep import BRep_Tool
from OCC.Core.AIS import AIS_Shape
# from OCC.Core.TopTools import Top
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
# from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import (
    gp_Pnt, gp_Vec, gp_Trsf, gp_Ax2, gp_Ax3, gp_Pnt2d, gp_Dir2d, gp_Ax2d, gp_Pln, gp_Circ, gp_Dir, gp_Lin
)
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire, BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Section
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.STEPControl import STEPControl_Reader, STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static
from OCC.Core.GeomAPI import GeomAPI_IntSS
from OCC.Extend.DataExchange import read_step_file
from OCCUtils.Construct import make_polygon, make_wire, make_vertex
from OCCUtils.Common import minimum_distance
from math import pi

display, start_display, add_menu, add_function_to_menu = init_display()

shp = read_step_file("../assets/models/face_recognition_sample_part.stp"
                     # os.path.join("..", "assets", "models", "face_recognition_sample_part.stp")
                     )


def section():
    # orign_profile = create_original(filename)
    sections = []
    for body in range(3):
        section_shp = BRepAlgoAPI_Section(shp,
                                          gp_Pln(gp_Pnt(0, 0, body + 1),
                                                 gp_Dir(0, 0, 1)),
                                          False)
        section_shp.ComputePCurveOn1(True)
        section_shp.Approximation(True)
        section_shp.Build()
        section_edge = section_shp.SectionEdges()
        print(section_edge.Size())
        sections.append(section_shp)

    display.EraseAll()
    display.DisplayShape(shp)
    for section_ in sections:
        display.DisplayShape(section_.Shape())
    display.FitAll()
    return sections


def sect_edges():
    # Obtaining the intersecting edges from the sections
    sectioning = section()
    print(sectioning)
    # We loop through each sections created
    thewires = []
    for i in range(len(sectioning)):
        intersect_edges = sectioning[i].SectionEdges()  # obtaining the edges
        wire_builder = BRepBuilderAPI_MakeWire()
        # Iterate over the edges and add them to the wire builder
        print(intersect_edges.First(),
              intersect_edges.Last(), intersect_edges.Size())
        list_edges = []
        it = TopTools_ListIteratorOfListOfShape(intersect_edges)
        while it.More():
            list_edges.append(it.Value())
            it.Next()
        for inter_edge in list_edges:
            # topo_edge = TopoDS_Edge(inter_edge)
            wire_builder.Add(inter_edge)
#
        # Check if the wire is valid
        if wire_builder.IsDone():
            wire = wire_builder.Wire()
            thewires.append(wire)
#
            # Create an AIS_Shape for visualization
            anAisWire = AIS_Shape(wire)
            anAisWire.SetWidth(2.0)
#
            # Display the wire
            display.Context.Display(anAisWire, True)
        else:
            print("Error: Wire creation failed")
    return thewires


edgex = sect_edges()
print(edgex)

pts = [
    gp_Pnt(-1, -1, 0),
    gp_Pnt(10, 10, 0),
    gp_Pnt(10, 10, 20),
    # gp_Pnt(30, 40, 1),
]
wire = make_polygon(pts, closed=True)
axis = gp_Ax3(gp_Pnt(200, -100, -200), gp_Dir(0, 1, 0))
trsf = gp_Trsf()
trsf.SetTransformation(gp_Ax3(), axis)
axs = gp_Ax3()
axs.Transform(trsf)
wire.Move(TopLoc_Location(trsf))
display.DisplayShape(wire)
display.DisplayShape(axs.Location())
print(axs.Location())


from OCC.Core.BRepProj import BRepProj_Projection
proj = BRepProj_Projection(wire, shp, gp_Dir(0, 1, 0))
list_wire = []
while proj.More():
    poly = proj.Current()
    list_wire.append(
        [minimum_distance(make_vertex(axs.Location()), poly)[0], poly])
    proj.Next()
    display.DisplayShape(poly, color="BLUE1")
list_wire.sort(key=lambda e: e[0])


from OCC.Core.BRepIntCurveSurface import BRepIntCurveSurface_Inter
lin = gp_Lin(axs.Location(), gp_Dir(0, 1, 0))
api = BRepIntCurveSurface_Inter()
api.Init(shp, lin, 1.0E-9)
shp_int = []
while api.More():
    print(api.W())
    shp_int.append([api.W(), api.U(), api.V(), api.Pnt(),
                   api.Face(), api.Transition()])
    api.Next()
shp_int.sort(key=lambda e: e[0])

for i, p in enumerate(shp_int):
    print(p, list_wire[i])
    display.DisplayShape(p[3])


from OCC.Core.Geom import Geom_Line
glin = Geom_Line(lin)
for i, p1 in enumerate(shp_int[1:]):
    p0 = shp_int[i]
    p = glin.Value((p0[0] + p1[0]) / 2)


start_display()
