import numpy as np
import pandas as pd
import argiope

mesh = argiope.mesh.read_msh("data/dummy.msh")
path = "workdir/mesh.h5"
mesh.h5path = path
mesh.save()
del mesh
mesh = argiope.mesh.read_h5(path)

