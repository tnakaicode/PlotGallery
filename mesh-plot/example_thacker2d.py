"""
================================================================================
Thacker 2d
================================================================================

In this example, 2D thacker simulation is carried out. It consists of a planar surface
rotating in a paraboloid without friction. The free surface motion is periodic in time
and remains planar. One could think of water rotating in a paraboloïd glass.

.. note:: Analytical solution is given in: https://hal.archives-ouvertes.fr/hal-00628246/document at section 4.2.2, paragraph "Planar surface in a paraboloid".

"""

import os, sys
import argparse
import matplotlib.pyplot as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

#sphinx_gallery_thumbnail_number = 3

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()


################################################################################
#
# Parameters:
#--------------------

A = 1.
H0 = 0.1
ETA = 0.5
L = 4.

#Numerical scheme:
IPRES = True
SECOND_ORDER = True
NL = 2

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=4.5, time_iteration_max=10000,
                       second_order=SECOND_ORDER)

when = [0., 2.25, 4.5]
create_figure_scheduler = fk.schedules(times=when)

################################################################################
#
# Mesh:
#--------------------
dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
TG, vertex_labels, boundary_labels = fk.read_msh(dir_path + '/inputs/thacker2d.msh')
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)

x *= 0.4
y *= 0.4

triangular_mesh = fk.TriangularMesh(TG, vertex_labels, boundary_labels)

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh)

################################################################################
#
# Analytic solution:
#-----------------------------
#
#Analytic solution is defined in a Thacker2D class with h0 being the
#water depth at the central point of the domain for a zero elevation and a is
#the distance from this central point to the zero elevation of the shoreline.

thacker2d_analytic = fk.Thacker2D(triangular_mesh, a=A, h0=H0, eta=ETA, L=L,
                                  scheduler=fk.schedules(times=when), NL=NL)

################################################################################
#
# The topography is defined in freshkiss3d.extra.analyticsol.Thacker2D so that:
#
#.. math:: z(r) = -h_0 \left( 1 - \frac{r^2}{a^2} \right)
#
#.. math:: r = \sqrt{(x-L/2)^2 + (y-L/2)^2}

thacker2d_analytic(0.)

################################################################################
#
# Analytic solution is computed with the following formula:
#
#.. math::
#   \begin{cases}
#   h(x,y,t) = \frac{\eta h_0}{a^2} \left( 2\left( x- \frac{L}{2} \right) \cos (\omega t) + 2\left( x- \frac{L}{2} \right) \sin (\omega t) - \eta \right) - z(x,y) \\
#   u(x,y,t) = - \eta \omega \sin( \omega t ) \\
#   v(x,y,t) = \eta \omega \cos( \omega t )
#   \end{cases}
#

################################################################################
#
# with:
#
#.. math:: \omega = \sqrt{2g h_0}/a \quad \text{and} \quad  \eta = 0.5

################################################################################
#
#.. warning::
#   Analytic solution is available in Thacker2d for single layer St Venant only

################################################################################
#
# Layers:
#--------------------
#
#.. note:: Topography defined in thacker2d is shared with layer
#

layer = fk.Layer(NL, triangular_mesh, topography=thacker2d_analytic.topography)

################################################################################
#
# Primitives:
#--------------------
#
#.. note:: H, U and V are initialized with analytic initial solution
#

primitives = fk.Primitive(triangular_mesh, layer,
                          height=thacker2d_analytic.H,
                          Uinit=thacker2d_analytic.U,
                          Vinit=thacker2d_analytic.V)

################################################################################
#
#Topography and initial height computed in thacker2d_analytic are
#the following:

def Topo(x, y):
    r2 = (x - 0.5*L)**2 + (y-0.5*L)**2
    return - H0 * (1 - (r2/A**2))

def H_0(x, y):
    return ETA * H0 / A**2 * (2* (x-0.5*L) - ETA) - Topo(x, y)

if not args.nographics:
  fk_plt.plot_init_1d_slice(triangular_mesh, surf_xy=H_0, topo_xy=Topo, surface_type='height')

################################################################################
#
# Boundary conditions:
#---------------------

fluvial_heights = [fk.FluvialHeight(ref=r, height=0.0) for r in [1, 2, 3, 4]]

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     fluvial_heights=fluvial_heights,
                     analytic_sol=thacker2d_analytic,
                     numerical_parameters={'ipres':IPRES,'space_second_order':SECOND_ORDER},
                     custom_funct={'plot':fk_plt.plot_freesurface_3d_analytic_2},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#
# Problem solving:
#-----------------
#
#When a figure plot is scheduled thacker2d.compute is called to compute analytic solution.

problem.solve()

if not args.nographics:
  plt.tight_layout()
  plt.show()
