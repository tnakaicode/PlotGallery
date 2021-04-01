import numpy as np
import pandas as pd
import argiope

mesh = mesh = argiope.indentation.sample_mesh_2D("gmsh", "./workdir/")
argiope.mesh.write_xdmf(mesh, "workdir/mesh")
