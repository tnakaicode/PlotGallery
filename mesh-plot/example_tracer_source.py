"""
================================================================================
Tracer source
================================================================================

In this example, a pollutant is released and convected in a river. The flow in the
river is subcritical and boundary conditions are fluvial flowrate for inlet and fluvial
height for outlet. Pollutant is defined as a tracer and its release into the river
is modelled with fk.TracerSource external effect i.e. a quantity of tracer is realeased
at given times in designated cells.

"""
import os, sys
import argparse
import numpy as np
import matplotlib.pylab as plt
import matplotlib.tri as mtri
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

FINAL_TIME = 50.

simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=10000,
                       second_order=False)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/river_polluant.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

################################################################################
#
# Layers:
#--------------------

NL = 4
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#
# Primitives:
#--------------------

primitives = fk.Primitive(triangular_mesh, layer, free_surface=2.)

################################################################################
#
# Tracer:
#---------------------
#
################################################################################
#
#.. important::
#
#   Let us define two tracers, labeled ``polluant_0`` and ``polluant_1``. Labels are
#   very important to link boundary conditions as well as source terms to the correct
#   tracer in the code.

tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit=0., label='polluant_0'),
           fk.Tracer(triangular_mesh, layer, primitives, Tinit=10., label='polluant_1')]

################################################################################
#
# Boundary conditions:
#---------------------
#
#Boundary conditions are the same as in reiver example excepts we define inlet
#flowrate in a input file.

times, flowrates = np.loadtxt('inputs/river_polluant_flowrate.txt', unpack=True)
flowrate = fk.TimeDependentFlowRate(times=times, flowrates=flowrates)

fluvial_flowrates = [fk.FluvialFlowRate(
    ref=1, time_dependent_flowrate=flowrate, x_flux_direction=1.0, y_flux_direction=0.0,
    tracers_inlet={'polluant_0':0., 'polluant_1':10.})]

fluvial_heights = [fk.FluvialHeight(
    ref=2, height=2., tracers_inlet={'polluant_0':0., 'polluant_1':10.})]

slides = [fk.Slide(ref=3)]

################################################################################
#
#.. note::
#   Note that tracer labels have been used to provide tracer value at inlet
#   boundary condition. In our case, we provide the same boundary condition inlet 
#   values as for tracer initialization.

################################################################################
#
# External effects (tracer source terms):
#----------------------------------------
#
#``ExternalEffects`` objects are called in ``problem.solve()`` at each time step. In
#this example external effects are ``TracerSource``.
#There can be as much external effects as needed as long as they are stored in a
#dictionary.
#
#``TracerSource`` can have different unit based on the way you want it to be applied.
#
# * If ``source_unit='[T]/s'``: tracer source is continuous over time, and is applied at each time step. In this case tracer source value is interpolated linearly from ``sources`` and ``times`` parameters.
# * If ``source_unit='[T]'``: tracer source is sparse over time, and is applied only on specified ``times`` with the corresponding value of ``sources``.
#

polluant_source_0 = fk.TracerSource(
    times=[1., FINAL_TIME],
    sources=[20, 20],
    source_unit='[T]/s',
    tracer_label='polluant_0',
    cells=[607])

polluant_source_1 = fk.TracerSource(
    times=[1, 10, 20, 30],
    sources=[20, 20, 20, 20],
    source_unit='[T]',
    tracer_label='polluant_1',
    cells=[617])

external_effects = {"continuous": polluant_source_0, "sparse": polluant_source_1}

################################################################################
#
#.. note::
#
#   * Once again, tracer labels are used to apply source terms on each one of the tracers.
#   * Note that tracer sources can be set in kg instead of [T]=kg/m3 in the case of species. The corresponding concentration source term is computed based on cell volume and mass source.

################################################################################
#
# Writter: 
#---------------------- 
#

NB_VTK = 10
vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=NB_VTK),
                          scale_h=5.)

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     fluvial_heights=fluvial_heights,
                     fluvial_flowrates=fluvial_flowrates,
                     tracers=tracers,
                     external_effects=external_effects,
                     vtk_writer=vtk_writer)

################################################################################
#
# Problem solving:
#-----------------

problem.solve()

################################################################################
#
# Basic plots:
#------------------
#
if not args.nographics:

  x = np.asarray(triangular_mesh.triangulation.x)
  y = np.asarray(triangular_mesh.triangulation.y)
  trivtx = np.asarray(triangular_mesh.triangulation.trivtx)
  triang = mtri.Triangulation(x, y, trivtx)

  LAYER_IDX = [int(NL/3), int(2*NL/3)]

  plt.rcParams["figure.figsize"] = [8, 10]
  fig = plt.figure()

  ax1 = fig.add_subplot(211)
  T0 = problem.tracers[0].T[:, LAYER_IDX[1]]
  v = np.linspace(min(T0), max(T0), 20, endpoint=True)
  ax1.triplot(x, y, trivtx, color='k', lw=0.5)
  im1 = ax1.tricontourf(x, y, trivtx, T0, v, cmap=plt.cm.jet)
  fig.colorbar(im1, ax=ax1, ticks=v)
  ax1.set_title("Tracer 0 on layer {}".format(LAYER_IDX[1]))

  ax1b = fig.add_subplot(212)
  T1 = problem.tracers[1].T[:, LAYER_IDX[1]]
  v = np.linspace(min(T1), max(T1), 20, endpoint=True)
  ax1b.triplot(x, y, trivtx, color='k', lw=0.5)
  im1b = ax1b.tricontourf(x, y, trivtx, T1, v, cmap=plt.cm.jet)
  fig.colorbar(im1b, ax=ax1b, ticks=v)
  ax1b.set_title("Tracer 1 on layer {}".format(LAYER_IDX[1]))
  plt.show()
