import numpy as np
import pandas as pd
import argiope

mesh = argiope.indentation.sample_mesh_2D("gmsh", "./workdir/")
#argiope.mesh.write_inp(mesh, "workdir/mesh.inp")
element_map = {"Tri3":  "CAX3", 
               "Quad4": "CAX4", }
mesh.to_inp(path = "workdir/mesh.inp", element_map = element_map)
