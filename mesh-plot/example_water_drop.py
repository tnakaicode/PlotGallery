"""
================================================================================
Water drop
================================================================================

This case is a simple water drop showing the ability of freshkiss3d to simulate
wave propagation and reflections on solid boundaries.

"""

import os, sys
import matplotlib.pylab as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

#sphinx_gallery_thumbnail_number = 3

################################################################################
#
# Parameters:
#----------------------
#

NUM_PARAMS={'ipres':True,
            'space_second_order':False,
            'flux_type':2,
            'implicit_exchanges':True,
            'implicit_vertical_viscosity':True}

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=4., time_iteration_max=20000, second_order=True)

create_figure_scheduler = fk.schedules(times=[0., 1., 2., 3., 4., 5.])

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/square2.mesh')

fk_plt.plot_mesh(triangular_mesh)

################################################################################
#
# Layers:
#--------------------

NL = 1
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#
# Primitives:
#--------------------
#
#Initial height is set with a user defined function.
 
def H_0(x, y):
    h = 2.4*(1.0 + np.exp(-0.25*((x-10.05)**2+(y-10.05)**2)))
    return h

primitives = fk.Primitive(triangular_mesh, layer, height_funct=H_0)

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#
# Writter:
#----------------------
#

vtk_writer = fk.VTKWriter(triangular_mesh,
                          scheduler=fk.schedules(count=10), scale_h=1.)

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     numerical_parameters=NUM_PARAMS,
                     vtk_writer=vtk_writer,
                     custom_funct={'plot':fk_plt.plot_freesurface_3d},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#
# Problem solving:
#-----------------

problem.solve()
plt.show()
