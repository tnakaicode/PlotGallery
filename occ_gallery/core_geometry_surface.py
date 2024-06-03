# -*- coding: utf-8 -*-
from OCC.Core.BOPAlgo import BOPAlgo_Splitter
from OCC.Core.gp import gp_Pnt
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Core.BRep import BRep_Tool
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeVertex,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
)

from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()

coords = [
    (-20, -20, 0),
    (-20, 20, 0),
    (20, 20, 0),
    (20, -20, 0)
]
# Create vertices
vertices = list()
for coord in coords:
    vertices.append(BRepBuilderAPI_MakeVertex(gp_Pnt(*coord)).Shape())
# Join vertices to create a closed loop of edges
nv = len(vertices)
edges = list()
for i in range(0, nv, 1):
    if i < nv - 1:
        edge = BRepBuilderAPI_MakeEdge(vertices[i], vertices[i + 1]).Shape()
    elif i == nv - 1:
        edge = BRepBuilderAPI_MakeEdge(vertices[i], vertices[0]).Shape()
    else:
        raise ValueError('Out of bounds, i=', i)
    edges.append(edge)
a_maker = BRepBuilderAPI_MakeWire()
for edge in edges:
    a_maker.Add(edge)
a_maker.Build()
original_topods_wire = a_maker.Shape()
OnlyPlane = True
a_maker = BRepBuilderAPI_MakeFace(original_topods_wire, OnlyPlane)
a_maker.Build()
a_topods_face = a_maker.Shape()

# Create an edge based on two points
p1 = gp_Pnt(0, -20, 0)
p2 = gp_Pnt(0, 20, 0)
a_topods_edge = BRepBuilderAPI_MakeEdge(p1, p2).Edge()

# Split the geom face face by edge
splitter = BOPAlgo_Splitter()
splitter.AddArgument(a_topods_face)
splitter.AddTool(a_topods_edge)
splitter.Perform()

# Get one of the resulting topods face - works fine
faces = TopologyExplorer(splitter.Shape()).faces()
print(faces)
# my_renderer = JupyterRenderer()
for face in faces:
    a_topods_split_face = face
print(a_topods_split_face)
# display.DisplayShape(a_topods_split_face, update=True)

# Convert the trimmed topods face to  geom surface
a_geom_surface_after_conversion = BRep_Tool.Surface(a_topods_split_face)
print(a_geom_surface_after_conversion)
check_the_face = BRepBuilderAPI_MakeFace(a_geom_surface_after_conversion,
                                         1e-6).Face()
print(check_the_face)
# my_renderer = JupyterRenderer()
display.DisplayShape(check_the_face, update=True)   # nothing displayed
start_display()
