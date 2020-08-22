"""
================================================================================
Dam break
================================================================================

In this example the classic test of the dambreak for the Saint-Venant system is illustrated.
Comparison between 2D numerical solution and 1D analytical solution is carried out
for the wet and dry dambreak cases.

.. note::
   1D analytical solutions are given in: https://hal.archives-ouvertes.fr/hal-00628246/document at section 4.1, paragraph "Dam breaks".

"""

import os, sys
import argparse
import matplotlib.pylab as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 3

################################################################################
#
# Riemann problems:
#--------------------
#
# Two cases (Riemann problems) are considered in this example:
#
#- Dam break on a wet domain without friction (case = 'wet')
#
#    .. math::
#       h(x) = \begin{cases}
#       h_l \quad \text{for} \quad 0 \leq x \leq x_d \\
#       h_r \quad \text{for} \quad x_d < x \leq L
#       \end{cases}
#
#- Dam break on a dry domain without friction (case = 'dry')
#
#    .. math::
#       h(x) = \begin{cases}
#       h_l > 0 \quad \text{for} \quad 0 \leq x \leq x_d \\
#       h_r = 0 \quad \text{for} \quad x_d < x \leq L
#       \end{cases}
#

CASE = 'wet'

if CASE == 'wet':
    H_L = 0.005
    H_R = 0.001
elif CASE == 'dry':
    H_L = 0.005
    H_R = 0.

FINAL_TIME = 10.
X_D = 5

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=100000,
                       second_order=True)

# Plot figure scheduler:
WHEN = [FINAL_TIME/2., FINAL_TIME-1.]
create_figure_scheduler = fk.schedules(times=WHEN)


################################################################################
#
# Mesh:
#--------------------
# .. math::
#
#     L = 10 m, l = 0.5 m
#

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path+'/inputs/dambreak.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

################################################################################
#
# 1D Analytic solutions:
#-----------------------------
#
# 1D analytic solution is defined in a DamBreak class. Computation of the solution 
# depends on initial height values on each side of the dam.
#

dambreak_analytic = fk.DamBreak(triangular_mesh, 
                                h_l=H_L,
                                h_r=H_R,
                                x_d=X_D,
                                scheduler=fk.schedules(times=WHEN))
dambreak_analytic(0.)

################################################################################
#
#- In the 'wet' case analytical solution is given by:
#
#.. math::
#   h(x,t) = \begin{cases}
#   h_l \quad & \text{if} \quad x \leq x_A(t) \\
#   \dfrac{4}{9g} \left( \sqrt{gh_l} - \dfrac{x-x_0}{2t} \right)^2 \quad & \text{if} \quad x_A(t) \leq x \leq x_B(t) \\
#   \dfrac{c_m^2}{9} \quad & \text{if} \quad x_B(t) \leq x \leq x_C(t) \\
#   h_r \quad & \text{if} \quad x_C(t) \leq x
#   \end{cases}
#
#.. math::
#   u(x,t) = \begin{cases}
#   0 \quad & \text{if} \quad x \leq x_A(t)\\
#   \dfrac{2}{3} \left( \dfrac{x-x_0}{t} + \sqrt{gh_l} \right) \quad & \text{if} \quad x_A(t) \leq x \leq x_B(t) \\
#   2 \left( \sqrt{gh_l} - c_m\right) \quad & \text{if} \quad x_B(t) \leq x \leq x_C(t)\\
#   0 \quad & \text{if} \quad x_C(t) \leq x
#   \end{cases}
#
#.. math::
#   \begin{cases}
#   x_A(t) = x_0 - t \sqrt{g h_l} \\
#   x_B(t) = x_0 + t \left( 2 \sqrt{gh_l} - 3c_m \right) \\
#   x_C(t) = x_0 + t \left( \dfrac{2c_m^2 \left( \sqrt{gh_l} - c_m \right)}{c_m^2-g h_r} \right)
#   \end{cases}
#
#.. math:: c_m \quad \text{being solution of} \quad -8g h_r c_m^2 (\sqrt{gh_l}-c_m)^2+(c_m^2-gh_r)^2(c_m^2+gh-r)
#

################################################################################
#
#- If case is set to 'dry' analytical solution is given by:
#
#.. math::
#   h(x,t) = \begin{cases}
#   h_l \quad & \text{if} \quad x \leq x_A(t) \\
#   \dfrac{4}{9g} \left( \sqrt{gh_l} - \dfrac{x-x_0}{2t} \right)^2 \quad & \text{if} \quad x_A(t) \leq x \leq x_B(t) \\
#   0 \quad & \text{if} \quad x_B(t) \leq x
#   \end{cases}
#
#
#.. math::
#   u(x,t) = \begin{cases}
#   0 \quad & \text{if} \quad x \leq x_A(t) \\
#   \dfrac{2}{3} \left( \dfrac{x-x_0}{t} + \sqrt{gh_l} \right) \quad & \text{if} \quad x_A(t) \leq x \leq x_B(t)\\
#   0 \quad & \text{if} \quad x_B(t) \leq x
#   \end{cases}
#
#.. math::
#   \begin{cases}
#   x_A(t) = x_0 - t \sqrt{g h_l} \\
#   x_B(t) = x_0 + 2t \sqrt{gh_l} \\
#   \end{cases}
#

################################################################################
#
#.. warning::
#   Analytic solution is available in DamBreak for single layer, 1D St Venant only
#

################################################################################
#
# Layers:
#--------------------
#
#Number of layers is set to one for comparison with analytical solutions.
#

NL = 1
layer = fk.Layer(NL, triangular_mesh, topography=dambreak_analytic.topography)

################################################################################
#
# Primitives:
#--------------------

def h_0(x, y):
    h = H_R
    if x < X_D: h = H_L
    return h

if not args.nographics:
  fk_plt.plot_init_1d(triangular_mesh, h_0, 'x', '$H_0$')

primitives = fk.Primitive(triangular_mesh, layer,
                          height_funct=h_0,
                          Uinit=0.,
                          Vinit=0.)

################################################################################
#
# Boundary conditions:
#---------------------

fluvial_heights = [fk.FluvialHeight(ref=1, height=H_L), 
                   fk.FluvialHeight(ref=2, height=H_R)]
slides = [fk.Slide(ref=3), fk.Slide(ref=4)]

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh,
                     layer, primitives,
                     fluvial_heights=fluvial_heights,
                     slides=slides,
                     numerical_parameters={'space_second_order':False},
                     analytic_sol=dambreak_analytic,
                     custom_funct={'plot':fk_plt.plot_freesurface_3d_analytic},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#
# Problem solving:
#-----------------

problem.solve()

if not args.nographics:
  plt.show()
