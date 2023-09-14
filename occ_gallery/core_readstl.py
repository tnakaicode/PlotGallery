from tqdm import tqdm

import numpy as np
from stl import mesh
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Builder
from OCC.Core.gp import gp_Pnt


def stl_to_shape(stl_filename):
    # Read the STL using numpy-stl
    stl_mesh = mesh.Mesh.from_file(stl_filename)

    # Create an empty compound to hold the resulting triangles
    compound = TopoDS_Compound()
    builder = TopoDS_Builder()
    builder.MakeCompound(compound)

    # Iterate over the facets in the STL
    for facet in tqdm(stl_mesh.vectors, desc="processing facets"):
        # Create a polygon for each triangle in the STL
        polygon = BRepBuilderAPI_MakePolygon()
        for vertex in facet:
            x, y, z = map(float, vertex)
            polygon.Add(gp_Pnt(x, y, z))
        polygon.Close()

        # Create a face from the polygon and add it to the compound
        face = BRepBuilderAPI_MakeFace(polygon.Wire()).Face()
        builder.Add(compound, face)

    return compound


if __name__ == "__main__":
    stl_to_shape("../assets/models/fan.stl")
