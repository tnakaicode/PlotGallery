"""
================================================================================
Riemann problem 2d
================================================================================

This case is a simple Riemann problem in 2D. Geometry is a square which is split in four.
On each part initial height is set to a constant value. Initial velocity is null
and all sides are walls.

"""
import os, sys
import argparse
import pylab as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=5., time_iteration_max=2000, second_order=True)

create_figure_scheduler = fk.schedules(times=[1., 2., 3., 4., 5.])

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/square.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

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
    h = 1.
    if x < 2.5 and y < 2.5: h = 4.
    if x < 2.5 and y > 2.5: h = 3.
    if x > 2.5 and y < 2.5: h = 1.
    if x > 2.5 and y > 2.5: h = 2.
    return h

if not args.nographics:
  fk_plt.plot_init_3d(triangular_mesh, H_0)

primitives = fk.Primitive(triangular_mesh, layer, height_funct=H_0)

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     numerical_parameters={'ipres':True, 'space_second_order':True},
                     custom_funct={'plot':fk_plt.plot_height_2d_3d},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#
# Problem solving:
#-----------------

problem.solve()

if not args.nographics:
  plt.show()
