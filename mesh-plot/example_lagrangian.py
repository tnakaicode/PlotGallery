"""
================================================================================
Lagrangian
================================================================================

In this example Lagrangian particle tracking capabilities of Freshkiss3D are
illustrated. A cavity with wind forcing is initialy filled with a distribution
of particles. Particles' motion is computed and plotted with paraview.

"""

import os, sys
import argparse
import matplotlib.pylab as plt
import matplotlib.image as mpimg
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Time loop:
#--------------------

FINAL_TIME = 250. #1500.
simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=200000, second_order=False)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
TG, vertex_labels, boundary_labels = fk.read_msh(dir_path + '/inputs/simple_canal_2.msh')
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)
x *= 10
y *= 10
triangular_mesh = fk.TriangularMesh(TG, vertex_labels, boundary_labels)

# Set neighbours (needed for lagrangian setup)
triangular_mesh.set_neighbours()

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

################################################################################
#
# Layers:
#--------------------

NL = 20
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#
# Primitives:
#--------------------
#
#Initial height is defined thanks to a user defined function.

primitives = fk.Primitive(triangular_mesh, layer, height=2., Uinit=0., Vinit=0.)

################################################################################
#
# Particles:
#--------------------
#
#Lagrangian particle tracking is carried out with a Lagrangian class that users
#have to define and pass to the Problem class.
#Initial position of particles can either be defined by the ``generate_homogeneous_positions``
#function provided in freshkiss3d or by a custom user defined function. Lagrangian
#class is initialized with a ``positions`` matrix of dimension [Npart,3] containing
#x, y, z coordonates of each particle.

def generate_positions(n):
    pos = []
    y_0 = 2.5
    xgrid = np.linspace(0.5, 19.5, n)
    zgrid = np.linspace(0.1, 1.9, 5)
    for I in range(len(xgrid)):
        for J in range(len(zgrid)):
            pos.append([xgrid[I], y_0, zgrid[J]])
    return np.asarray(pos)

positions = generate_positions(10)

#positions = fk.generate_homogeneous_positions(triangular_mesh, layer, primitives,
#                                              npart= 50)

lagrangian = fk.Lagrangian(positions, triangular_mesh, layer, primitives)

################################################################################
#
#.. note::
#   Outputs are generated in vtk with the ``VTKWriter`` class and with the same
#   scheduler unless you provide the lagrangian class with a proper scheduler.
#   See API for more info on Lagrangian parameters.

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#
# Wind forcing:
#---------------------

WIND_FORCING = True
WIND_VELOCITY = 50

wind_effect = fk.WindEffect(velocity=[WIND_VELOCITY, WIND_VELOCITY],
                            orientation=[270., 270.],
                            times=[0., 10.])
if WIND_FORCING:
    external_effects = {"wind": wind_effect}
    PHY_PARAMS={'friction_coeff':1.,
                'horizontal_viscosity':.1,
                'vertical_viscosity':.1}
else:
    PHY_PARAMS = {}

################################################################################
#
# Tracer:
#--------------------

def T_0(x, y):
    if x > 10:
        T0 = 100
    else:
        T0 = 0.0
    return T0

tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit_funct=T_0)]

################################################################################
#
# Writter:
#----------------------
#

NB_VTK = 10
vtk_writer = fk.VTKWriter(triangular_mesh,
                          scheduler=fk.schedules(count=NB_VTK),
                          scale_h=5.)

txt_writer = fk.TXTWriter([84], scheduler=fk.schedules(count=5))

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     lagrangian=lagrangian,
                     tracers=tracers,
                     external_effects=external_effects,
                     numerical_parameters={'space_second_order':False},
                     physical_parameters=PHY_PARAMS,
                     vtk_writer=vtk_writer,
                     txt_writer=txt_writer)

################################################################################
#
# Problem solving:
#-----------------
problem.solve()

################################################################################
#
# Post-processing with paraview:
#--------------------------------
#

os.system('python2.7 postpro_paraview/postpro_lagrangian.py -n {}'.format(NB_VTK))

################################################################################
#
#.. note::
#    To be able to use paraview post-processing scripts you need to install python2.7
#    (outside conda envs. fk) and add the following lines to your ``.bashrc``:
#
#    .. code-block:: bash
#
#       export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/site-packages
#       export PYTHONPATH=$PYTHONPATH:/usr/lib/paraview/site-packages
#
#    With the command ``os.system('')`` paraview post-processing script ``postpro_settling.py``
#    located in the ``/paraview`` subfolder is called.
#    This script creates a ``.png`` file that can then be retrieved and manipulated with matplotlib.

if not args.nographics:
  plt.style.use('seaborn-white')
  plt.rcParams['font.family'] = 'serif'
  plt.rcParams['font.size'] = 14
  plt.rcParams['axes.labelsize'] = 12
  plt.rcParams['axes.labelweight'] = 'bold'
  plt.rcParams['axes.titlesize'] = 14
  plt.rcParams['xtick.labelsize'] = 10
  plt.rcParams['ytick.labelsize'] = 10
  plt.rcParams['legend.fontsize'] = 12
  plt.rcParams['figure.titlesize'] = 16
  plt.rcParams["axes.grid"] = False
  plt.rcParams["figure.figsize"] = [6, 10]

  fig = plt.figure()

  ax1 = fig.add_subplot(211)
  im1 = mpimg.imread('outputs/lagrangian.png')
  ax1.imshow(im1, interpolation="spline16")
  ax1.set_title("Particles in 3D view at time={} s".format(FINAL_TIME))
  plt.setp(ax1.get_xticklabels(), visible=False)
  plt.setp(ax1.get_yticklabels(), visible=False)

  ax2 = fig.add_subplot(212)
  im2 = mpimg.imread('outputs/lagrangian_side.png')
  ax2.imshow(im2, interpolation="spline16")
  ax2.set_title("Particles in (x,z) plane at time={} s".format(FINAL_TIME))
  plt.setp(ax2.get_xticklabels(), visible=False)   
  plt.setp(ax2.get_yticklabels(), visible=False)

  plt.show()
