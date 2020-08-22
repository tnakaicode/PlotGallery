"""
=====================
Topography source
=====================

This is a simple topography source case showing the ability of freshkiss3d to apply
source terms on toporgaphy to simulate bed movement induced phenomena like tsunamis.

"""
import os, sys
import argparse
import numpy as np
import random as rd
import matplotlib.pylab as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

#sphinx_gallery_thumbnail_number = 5
parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

################################################################################
#
# Time loop:
#--------------------

FINAL_TIME = 20.
simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=20000, second_order=True)

create_figure_scheduler = fk.schedules(times=[0., 4., 6., 8.])

################################################################################
#  
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
TG, vertex_labels, boundary_labels = fk.read_msh(dir_path + '/inputs/square2.mesh')
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)

x *= 10.
y *= 10.

triangular_mesh = fk.TriangularMesh(TG, vertex_labels, boundary_labels)

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh)

################################################################################
#  
# Layers:
#--------------------

FREE_SURFACE = 8.0
X_1 = 10. ; X_2 = 100.
def topo(x, y):
    if x < X_1:
        topo = 10.0
    elif x > X_2:
        topo = 0.0
    else:
        topo = -(10.0/(X_2-X_1))*(x - X_2)
    return topo

NL = 2
layer = fk.Layer(NL, triangular_mesh, topography_funct=topo)

################################################################################
#  
# Primitives:
#--------------------
#
 
primitives = fk.Primitive(triangular_mesh, layer, free_surface=FREE_SURFACE)

if not args.nographics:
  fk_plt.plot_init_1d_slice(triangular_mesh, surf=FREE_SURFACE, topo_xy=topo)

################################################################################
#  
# Topography source term: 
#------------------------
#
#``ExternalEffects`` objects are called in ``problem.solve()`` at each time step. In
#this example external effects are ``TopographySource``.
#There can be as much external effects as needed as long as they are stored in a
#dictionary type.
#
#Let us consider two cases:
#
# * In the first case we define continuous topography source over time to simulate a slowly moving bed.
# * In the second case we define sparse topography source over time to simulate sudden motification of the bed like a landslide.
#
#.. note::
#   Note that in both cases (continuous or sparse over time), the source can either be 
#   homogeneous or heterogeneous in space i.e. user can set either a constant set of sources 
#   with the ``sources`` parameter or a function (or set of function) of x, y with
#   the ``sources_funct`` parameter. User can also set a vector of size (NC) containing
#   the source term on each cell of the mesh with the ``sources_cell`` parameter.
#

CASE = 2

if CASE == 1:
    # The bed movement rate in set in m/s with ``source_unit='m/s'``.
    def bed_source_rate(x, y, x_0=90., y_0=100.):
        return .2*np.exp(-.005*((x-(x_0+5.))**2+(y-y_0)**2)) \
             - .2*np.exp(-.005*((x-(x_0-5.))**2+(y-y_0)**2))

    if not args.nographics:
      fk_plt.plot_init_1d(triangular_mesh, bed_source_rate, 
                          absc='x', ordo='Bed source rate $m/s$', title='Source term')

    continuously_moving_bed = fk.TopographySource(
        times=[1., 10.],
        sources_funct=bed_source_rate,
        source_unit='m/s')
    external_effects = {"bed": continuously_moving_bed}

elif CASE == 2:
    # The landslide in set in m with ``source_unit='m'`` and occurs at :math:`t=1s`
    def landslide_source(x, y, x_0=90., y_0=100.):
        return 2.0*np.exp(-.005*((x-(x_0+5.))**2+(y-y_0)**2)) \
             - 2.0*np.exp(-.005*((x-(x_0-5.))**2+(y-y_0)**2))

    if not args.nographics:
      fk_plt.plot_init_1d(triangular_mesh, landslide_source, 
                          absc='x', ordo='Landslide source $m$', title='Source term')

    tsunami = fk.TopographySource(
        times=[1.],
        sources_funct=landslide_source,
        source_unit='m')
    external_effects = {"tsunami": tsunami}

else:
    external_effects = None

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=r) for r in [1,2,3,4]]

################################################################################
#
# Writter:
#----------------------
#

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=10),
                          scale_h=3.)

################################################################################
#  
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh,
                     layer, primitives,
                     slides=slides,
                     external_effects=external_effects,
                     vtk_writer=vtk_writer,
                     custom_funct={'plot':fk_plt.plot_freesurface_topo_3d},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#  
# Problem solving:
#-----------------

problem.solve()
if not args.nographics:
  plt.show()
