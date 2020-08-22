"""
================================================================================
River
================================================================================

In this example a flow in a bended river is considered. A simple configuration 
is chosen with water viscosity, Navier friction and flat topography.

This example purpose is to show the basic layout of frashkiss3d scripts.

"""
import os, sys
import argparse 
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.tri as mtri
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
# Parameters:
#--------------------

SECOND_ORDER=False

NUM_PARAMS={'ipres':True,
            'space_second_order':SECOND_ORDER,
            'flux_type':1}

PHY_PARAMS={'friction_law':'Navier',
            'friction_coeff':0.01,
            'horizontal_viscosity':0.0013,
            'vertical_viscosity':0.0013}

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=500., time_iteration_max=100000,
                       second_order=SECOND_ORDER)

################################################################################
#
# Mesh:
#--------------------
#
#Mesh is imported from mesh file located in /inputs directory.

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/river.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

################################################################################
#
# Layers:
#--------------------
#
#In this examlpe topography is flat all along the river.

NL = 8
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#
# Primitives:
#--------------------

primitives = fk.Primitive(triangular_mesh, layer, height=10.0)

################################################################################
#
# Boundary conditions:
#---------------------
#
#``FluvialFlowRate`` is set for inlet boundary condition and ``FluvialHeight`` for outlet.
#On side walls a ``Slide`` boundary condition is used with ``wall_friction_coeff``.

flowrate = fk.TimeDependentFlowRate(times=[0.0, 1000.0, 10000],
                                    flowrates=[0.0, 10.0, 10.0])

fluvial_flowrates = [fk.FluvialFlowRate(ref=2,
                                        time_dependent_flowrate=flowrate,
                                        x_flux_direction=1.0,
                                        y_flux_direction=0.0)]

fluvial_heights = [fk.FluvialHeight(ref=3, height=10.)]

slides = [fk.Slide(ref=1, horizontal_viscosity=PHY_PARAMS['horizontal_viscosity'],
                   wall_friction_coeff=PHY_PARAMS['friction_coeff'])]

################################################################################
#
# Writter:
#----------------------

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=10), scale_h=10.)

################################################################################
#
# Problem definition:
#--------------------
#
#Problem is called with basic parameters (simutime, mesh, layer, primitives and
#boundary conditions). See API for other useful ``fk.Problem`` parameters.

river = fk.Problem(simutime, triangular_mesh, layer, primitives,
                   slides=slides,
                   fluvial_flowrates=fluvial_flowrates,
                   fluvial_heights=fluvial_heights,
                   numerical_parameters=NUM_PARAMS,
                   physical_parameters=PHY_PARAMS,
                   vtk_writer=vtk_writer)

################################################################################
#
# Problem solving:
#-----------------

river.solve()

################################################################################
#
# Basic plots:
#------------------

if not args.nographics:

  x = np.asarray(triangular_mesh.triangulation.x)
  y = np.asarray(triangular_mesh.triangulation.y)
  trivtx = np.asarray(triangular_mesh.triangulation.trivtx)
  triang = mtri.Triangulation(x, y, trivtx)

  LAYER_IDX = int(NL/2)

  plt.rcParams["figure.figsize"] = [16, 6]
  fig = plt.figure()

  # Subplot 1: x velocity
  ax1 = fig.add_subplot(121)
  ax1.triplot(x, y, trivtx, color='k', lw=0.5)
  im1 = ax1.tricontourf(x, y, trivtx, river.primitives.U[:, LAYER_IDX], 30, cmap=plt.cm.jet)
  fig.colorbar(im1, ax=ax1)
  ax1.set_title("Velocity x component on layer {}".format(LAYER_IDX))

  # Subplot 2: y velocity
  ax2 = fig.add_subplot(122)
  ax2.triplot(x, y, trivtx, color='k', lw=0.5)
  im2 = ax2.tricontourf(x, y, trivtx, river.primitives.V[:, LAYER_IDX], 30, cmap=plt.cm.jet)
  fig.colorbar(im2, ax=ax2)
  ax2.set_title("Velocity y component on layer {}".format(LAYER_IDX))

  plt.show()

################################################################################
#
# Streamlines plot:
#------------------

if not args.nographics:

  plt.rcParams["figure.figsize"] = [8, 6]
  fig = plt.figure()
  ax1 = fig.add_subplot(111)
  xi, yi = np.meshgrid(np.linspace(0, 2000, 500),
                       np.linspace(0, 2000, 500))
  U_interp = mtri.LinearTriInterpolator(triang, river.primitives.U[:, LAYER_IDX])
  V_interp = mtri.LinearTriInterpolator(triang, river.primitives.V[:, LAYER_IDX])
  U_i = U_interp(xi, yi)
  V_i = V_interp(xi, yi)
  speed = np.sqrt(U_i**2 + V_i**2)
  ax1.set_xlim(0, 2000) 
  ax1.set_ylim(0, 2000)
  cmap = cm.get_cmap(name='jet', lut=None)
  strm = ax1.streamplot(xi, yi, U_i, V_i, density=(2, 2), color=speed, linewidth=2*speed/speed.max(), cmap=cmap)
  fig.colorbar(strm.lines)
  ax1.set_title("Velocity & Streamlines on layer {}".format(LAYER_IDX))

  plt.show()
