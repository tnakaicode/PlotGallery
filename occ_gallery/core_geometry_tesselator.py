import numpy as np

from OCC.Core.BRepPrimAPI import (
    BRepPrimAPI_MakeBox,
    BRepPrimAPI_MakeTorus,
    BRepPrimAPI_MakeCone,
)
from OCC.Core.Tesselator import ShapeTesselator
from OCCUtils.Construct import make_face, make_polygon
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

# use the tesselator to tesselate the shape
a_sphere = BRepPrimAPI_MakeCone(10, 20, 30).Shape()
a_sphere = BRepPrimAPI_MakeBox(10, 20, 30).Shape()
a_sphere = BRepPrimAPI_MakeTorus(100, 10).Shape()
sphere_tess = ShapeTesselator(a_sphere)
sphere_tess.Compute(True, 0.5)

sphere_triangle_set_string = sphere_tess.ExportShapeToX3DTriangleSet()
print("Triangle Set representation:")
print(sphere_triangle_set_string)
triangle_set = sphere_tess.GetVerticesPositionAsTuple()

# convert vertex coordinates to a numpy array
triangle_set_np_array = np.array(triangle_set)
nb = len(triangle_set_np_array)
# following should be 108
print("Number of floats in the numpy array:", nb)
# reshape the array to get an array of 3 float arrays
vertices = triangle_set_np_array.reshape((int(nb / 3), 3))
print(vertices)
print("Length of vertices array:", len(vertices))
# among all these vertices, there should only be 8 different
unique_vertices = np.unique(vertices, axis=0)
print("Number of unique vertices:", len(unique_vertices))
print("Unique vertices:\n", unique_vertices)

indices = [np.where(np.all(unique_vertices == ar, axis=1))[0][0] for ar in vertices]
print("Vertices indices:\n", indices)


# for xyz in vertices:
#    display.DisplayShape(gp_Pnt(*xyz))
for i in range(sphere_tess.ObjGetTriangleCount() - 1):
    idx = sphere_tess.GetTriangleIndex(i)
    # print(sphere_tess.ObjGetTriangleCount(),i,  idx)
    p0 = gp_Pnt(*sphere_tess.GetVertex(idx[0]))
    p1 = gp_Pnt(*sphere_tess.GetVertex(idx[1]))
    p2 = gp_Pnt(*sphere_tess.GetVertex(idx[2]))
    display.DisplayShape(make_face(make_polygon([p0, p1, p2], True)))
display.FitAll()
start_display()
