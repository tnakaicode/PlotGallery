"""
================================================================================
Convert mesh file to .msh format
================================================================================

"""

import os
import numpy as np
import matplotlib.pyplot as plt
import freshkiss3d as fk

################################################################################
#
# Convert a mesh file to ``.msh``
#--------------------------------
#
#To convert your mesh to ``.msh`` format simply call **fk.convert_to_msh(file_in, 
#file_out)** with file_in and file_out being:
#
#- **file_in**: targeted mesh
#- **file_out**: output file for which you have to choose a name

file_in = 'inputs/tiny_square.mesh'
file_out = 'inputs/tiny_square.msh'

fk.convert_to_msh(file_in, file_out)

################################################################################
#
#.. note::
#   Mesh conversion is compatible with MEDIT .mesh and GMSH .msh file_in format.
#

################################################################################
#  
# Check file conversion succeded
#-------------------------------

TG, vertex_labels, boundary_labels = fk.read_msh(file_out)
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)

plt.triplot(x, y, trivtx)
plt.show()

################################################################################
#
#Remove file_out which was only built for example purpose:
#

os.system('rm {}'.format(file_out))


