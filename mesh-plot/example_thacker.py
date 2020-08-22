"""
================================================================================
Thacker
================================================================================

Pseudo-1D thacker simulation.

"""

import os, sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

#sphinx_gallery_thumbnail_number = 2

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

################################################################################
#
# Parameters:
#--------------------

A = 1.
H = 0.1

#Numerical scheme:
SECOND_ORDER = True

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=4.6, time_iteration_max=2000,
                       second_order=SECOND_ORDER)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/thacker.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh)

################################################################################
#
# Topography:
#--------------------

def Topography(x, y):
    topo = -H * (1 - x**2/A**2)
    return topo

################################################################################
#
# Layers:
#--------------------

NL = 1
layer = fk.Layer(NL, triangular_mesh, topography_funct=Topography)

################################################################################
#
# Primitives:
#--------------------

def eta_0(x, y):
    h = -0.5*x + 4.0
    return h

def T_0(x, y):
    if x < -1.5:
        t = 35.0
    else:
        t = 0.0
    return t

#Plot initial free surface in (x,z) slice plane:
if not args.nographics:
  fk_plt.plot_init_1d_slice(triangular_mesh, surf_xy=eta_0, topo_xy=Topography, primitive_xy=T_0)

primitives = fk.Primitive(triangular_mesh, layer, free_surface_funct=eta_0)
tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit_funct=T_0)]

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=1), fk.Slide(ref=3)]
torrential_outs = [fk.TorrentialOut(ref=2)]
tube = fk.RectangularTube(xlim=(0.0, 4.0), ylim=(0.0, 6.0), zlim=(0.0, 6.0))
flowrate = fk.TimeDependentFlowRate(times=[0.0, 0.0], flowrates=[0.0, 0.0])
fluvial_flowrates = [fk.FluvialFlowRate(ref=4,
                                        time_dependent_flowrate=flowrate,
                                        rectangular_tube=tube,
                                        x_flux_direction=1.0,
                                        y_flux_direction=0.0)]

################################################################################
#
# Problem definition:
#--------------------

thacker = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     tracers=tracers,
                     slides=slides,
                     numerical_parameters={'space_second_order':SECOND_ORDER},
                     torrential_outs=torrential_outs,
                     fluvial_flowrates=fluvial_flowrates)

################################################################################
#
# Problem solving:
#-----------------

if not args.nographics:

  # Plot triangular mesh.
  TG = thacker.triangular_mesh.triangulation
  x = np.asarray(TG.x)
  y = np.asarray(TG.y)
  trivtx = np.asarray(TG.trivtx)

  # Plot y=5 line
  y5 = np.argwhere(np.isclose(thacker.triangular_mesh.vertices.y, 5))
  y5 = y5.flatten()

  # Plot topography
  plt.rcParams["figure.figsize"] = [10, 8]
  topo = np.asarray(thacker.layer.topography)
  plot_H = fk.TimeScheduler(np.linspace(0, 4.5, 10))
  H_figure, H_axes = plt.subplots(5, 2, sharex='col', sharey='row')
  H_axes = H_axes.T.flatten()

  # Time steping:
  while not thacker.simutime.is_finished:
    thacker.forward()
    if plot_H.now(thacker.simutime):
        H = np.asarray(thacker.primitives.H)
        ax = H_axes[plot_H.iteration]
        ax.plot(x[y5], topo[y5] + H[y5])
        ax.set_title("time = {:.1f}".format(thacker.simutime.time))
        ax.plot(x[y5], topo[y5], color='grey')
        ax.fill_between(x[y5], -0.5, topo[y5], facecolor='lightgrey', interpolate=True)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-0.5, 10)

  H_figure.subplots_adjust(hspace=0.5)
  plt.show()

  plt.rcParams["figure.figsize"] = [8, 6]
  plt.figure()
  plt.triplot(x, y, trivtx)
  plt.plot(x[y5], y[y5], 'ro')
