from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.Tesselator import ShapeTesselator

import numpy as np

# use the tesselator to tesselate the shape
a_sphere = BRepPrimAPI_MakeBox(10, 20, 30).Shape()
sphere_tess = ShapeTesselator(a_sphere)
sphere_tess.Compute()

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

indices = [np.where(np.all(unique_vertices == ar, axis=1))[0][0]
           for ar in vertices]
print("Vertices indices:\n", indices)
