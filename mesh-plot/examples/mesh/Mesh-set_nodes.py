import argiope as ag
import numpy as np

nlabels = np.arange(4) + 1 
coords = np.array([[0., 0., 0.],
                   [1., 0., 0.],
                   [1., 1., 0.],
                   [0., 1., 0.],])
                
mesh = ag.mesh.Mesh()
mesh.set_nodes(nlabels = nlabels, coords = coords)

