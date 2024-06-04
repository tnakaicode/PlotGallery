
from __future__ import print_function

import os
import os.path
import sys


from OCC.Core.STEPControl import STEPControl_Reader,STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static
from OCC.Core.TopTools import TopTools_ListOfShape
from OCC.Core.TopoDS import TopoDS_Edge
from OCC.Core.BRep import BRep_Tool
from OCC.Core.AIS import AIS_Shape
#from OCC.Core.TopTools import Top
from OCC.Core.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
from OCC.Core.GeomAbs import GeomAbs_Plane, GeomAbs_Cylinder
#from OCC.Core.TopoDS import topods_Face
from OCC.Core.BRepAdaptor import BRepAdaptor_Surface
from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import (
gp_Pnt, gp_Vec,gp_Trsf,gp_Ax2,gp_Ax3,gp_Pnt2d,gp_Dir2d,gp_Ax2d,gp_Pln,gp_Circ,gp_Dir
)
from OCC.Core.BRepBuilderAPI import (
BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire,BRepBuilderAPI_Transform
)
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism, BRepPrimAPI_MakeCylinder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut,BRepAlgoAPI_Section
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.STEPControl import STEPControl_Reader,STEPControl_Writer, STEPControl_AsIs
from OCC.Core.Interface import Interface_Static
from OCC.Core.GeomAPI import GeomAPI_IntSS
from OCC.Extend.DataExchange import read_step_file
from math import pi

display, start_display, add_menu, add_function_to_menu = init_display()

shp = read_step_file("./assets/models/face_recognition_sample_part.stp"
        #os.path.join("..", "assets", "models", "face_recognition_sample_part.stp")
    )

def section():
    orign_profile = create_original(filename)
    sections = []
    for body in orign_profile:
        section_shp = BRepAlgoAPI_Section(shp, body, False)
        section_shp.ComputePCurveOn1(True)
        section_shp.Approximation(True)
        section_shp.Build()
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
    #We loop through each sections created
    thewires=[]
    for i in range(len(sectioning)):
        intersect_edges = sectioning[i].SectionEdges()#obtaining the edges
        wire_builder = BRepBuilderAPI_MakeWire()
        # Iterate over the edges and add them to the wire builder
        for inter_edge in intersect_edges:
            topo_edge = TopoDS_Edge(inter_edge)
            wire_builder.Add(topo_edge)

        # Check if the wire is valid
        if wire_builder.IsDone():
            wire = wire_builder.Wire()
            thewires.append(wire)

            # Create an AIS_Shape for visualization
            anAisWire = AIS_Shape(wire)
            anAisWire.SetWidth(2.0)

            # Display the wire
            display.Context.Display(anAisWire, True)
        else:
            print("Error: Wire creation failed")
    return thewires

edgex=sect_edges()
print(edgex)