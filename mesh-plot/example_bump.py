"""
================================================================================
Bump
================================================================================

In this example the classic test of the bump for the Saint-Venant system is illustrated.
Comparison between 2D numerical solution and 1D analytical solution is carried out
for three flow regimes.

.. note::
   1D analytical solutions are given in: https://hal.archives-ouvertes.fr/hal-00628246/document at section 3.1, paragraph "Bumps".

"""
import os, sys
import argparse
import numpy as np
import matplotlib.pylab as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Flow regimes: 
#--------------------
#
#From the properties of the single layer St Venant system (strict hyperbolicity) 
#we can deduce a classification of flows based on a criticality condition. 
#Let's first define the Froude number: 
#
#.. math::
#   \text{Fr} = \dfrac{|u|}{\sqrt{gh}} 
#
#The flow can be either subcritical or supercritical (Fr<1 and Fr>1 respectively). 
#For a given discharge another usefull quantity is the critical height defined by :
#
#.. math::
#   h_c = \left( \dfrac{q}{\sqrt{g}} \right)^{2/3}
# 
#The flow is subcritical and supercritical for h>h_c and h<h_c respectively
#

################################################################################
#
#In this example, several cases are considered depending on boundary conditions:
#
#- Subcritical flow
#- Transcritical flow without shock : the flow becomes torrential at the top of the bump.
#- Transcritical flow with shock : the flow becomes torrential at the top of the bump and fluvial again after the shock
#

FLOW = 'trans'

if FLOW == 'sub':
    FREE_SURFACE_0 = 0.7
    Q_IN = 0.2 
if FLOW == 'trans':
    FREE_SURFACE_0 = 0.7
    Q_IN = 1.5
if FLOW == 'trans_shock':
    FREE_SURFACE_0 = 0.33
    Q_IN = 0.18

H_OUT = FREE_SURFACE_0
FINAL_TIME = 1000.

################################################################################
#
# Time loop: 
#--------------------

simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=100000,
                       second_order=True)

# Plot figure scheduler:
WHEN = [FINAL_TIME-1.]
create_figure_scheduler = fk.schedules(times=WHEN)

################################################################################
#  
# Mesh: 
#--------------------
# .. math::
#
#     L = 25 m, l = 1 m 
#
dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path+'/inputs/bump.mesh')   

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh)

################################################################################
#
# 1D Steady state analytic solutions: 
#------------------------------------
# 
#1D steady state analytic solution is defined in a Bump class. 
#Computation of the solution depends on intial state, boundary conditions 
#and flow type. 
#The topography is defined as a function of x:
#

X_B = 10.
def topo(x):
    if 8.< x <12.:
        topo = 0.2 - 0.05*(x-X_B)**2
    else:
        topo = 0.0
    return topo

def topo_gaussian(x):
    topo = 0.25*np.exp(-0.5*(x-X_B)**2)
    return topo

bump_analytic = fk.Bump(triangular_mesh,
                        case=FLOW,
                        q_in=Q_IN,
                        h_out=H_OUT,
                        x_b = X_B,
                        free_surface_init=FREE_SURFACE_0,
                        topo = topo_gaussian,
                        scheduler=fk.schedules(times=WHEN))
bump_analytic(0.)

################################################################################
# 
#- In the 'subcritical' case, analytical solution is given by the resolution of: 
#
#   .. math:: 
#       h(x)^3 + \left( z(x) - \dfrac{q_0^2}{2g h(L)^2} - h(L) \right) h(x)^2 + \dfrac{q_0^2}{2g} = 0 \quad \forall x \in [0,L]
# 

################################################################################
# 
#- In the 'transcritical' case without shock, analytical solution is given by the resolution of: 
#
#   .. math:: 
#       h(x)^3 + \left( z(x) - \dfrac{q_0^2}{2g h_c^2} - h_c - z_M \right) h(x)^2 + \dfrac{q_0^2}{2g} = 0 \quad \forall x \in [0,L]    
# 
#   .. math:: \text{where  } z_M = \max_{x \in [0,L]}z
#

################################################################################
#
#- In the 'transcritical' case with shock, analytical solution is given by the resolution of: 
#
#   .. math:: 
#       \begin{cases}
#       h(x)^3 + \left( z(x) - \dfrac{q_0^2}{2g h_c^2} - h_c - z_M \right) h(x)^2 + \dfrac{q_0^2}{2g} = 0 \quad & \text{for  } x < x_{shock}  \\
#       h(x)^3 + \left( z(x) - \dfrac{q_0^2}{2g h(L)^2} - h(L) \right) h(x)^2 + \dfrac{q_0^2}{2g} = 0 \quad &\text{for  } x < x_{shock} \\
#       q_0^2 \left( \dfrac{1}{h(x_{shock}^-)} - \dfrac{1}{h(x_{shock}^+)} \right) + \dfrac{g}{2} \left( h(x_{shock}^-)^2 -h(x_{shock}^+)^2 \right) = 0
#       \end{cases}
#
#.. math:: \text{where the shock position is defined thanks to Rankine-Hugoniot's relation}
#

################################################################################
#
#.. warning::
#   Analytic solution is available in Bump for 1D steady state, single layer St Venant only
#

################################################################################
#  
# Layers: 
#--------------------
#
#Number of layers is set to one for comparison with analytical solutions.
#
#.. note:: Topography defined in ``fk.Bump`` is shared with ``fk.Layer``
#

NL=1
layer = fk.Layer(NL, triangular_mesh, topography=bump_analytic.topography)

################################################################################
#
# Primitives:
#--------------------

primitives = fk.Primitive(triangular_mesh, layer,
                          free_surface=FREE_SURFACE_0,
                          QXinit=Q_IN,
                          QYinit=0.)

################################################################################
#
# Boundary conditions:
#---------------------

fluvial_flowrates = [fk.FluvialFlowRate(ref=1,
                                        flowrate=Q_IN,
                                        x_flux_direction=1.0,
                                        y_flux_direction=0.0)]

fluvial_heights = [fk.FluvialHeight(ref=2, height=H_OUT)]
torrential_outs = [fk.TorrentialOut(ref=2)]

slides = [fk.Slide(ref=3), fk.Slide(ref=4)]

################################################################################
#
# Problem definition:
#--------------------

if FLOW == 'sub' or 'trans_shock':
    problem = fk.Problem(simutime, triangular_mesh,
                         layer, primitives, 
                         fluvial_flowrates=fluvial_flowrates,
                         fluvial_heights=fluvial_heights,
                         slides=slides,
                         numerical_parameters={'space_second_order':True},
                         analytic_sol=bump_analytic,
                         custom_funct={'plot':fk_plt.plot_freesurface_3d_analytic},
                         custom_funct_scheduler=create_figure_scheduler)

elif FLOW == 'trans':
    problem = fk.Problem(simutime, triangular_mesh, 
                         layer, primitives,
                         fluvial_flowrates=fluvial_flowrates,
                         torrential_outs=torrential_outs,
                         slides=slides,
                         numerical_parameters={'space_second_order':True},
                         analytic_sol=bump_analytic,
                         custom_funct={'plot':fk_plt.plot_freesurface_3d_analytic},
                         custom_funct_scheduler=create_figure_scheduler)

################################################################################
#  
# Problem solving:
#-----------------

problem.solve()

if not args.nographics:
  plt.show()
