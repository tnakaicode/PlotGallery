"""
================================================================================
Batch
================================================================================

In this tutorial batch run is illustrated.
River example is used as a basis for this tutorial.

"""

import matplotlib.pyplot as plt
import numpy as np
import freshkiss3d as fk

################################################################################
#
# Cases definition: 
#--------------------
#
#First of all cases need to be defined:
#

cases = [3, 6, 9]

PHY_PARAMS={'friction_law':'Navier',
            'friction_coeff':1.,
            'horizontal_viscosity':0.1,
            'vertical_viscosity':0.1}

################################################################################
#
#For any ``Problem`` input class we want to modify between cases, a list is created:
#

simutime_l = []
layer_l = []
primitives_l = []
friction_l = []
viscosity_l = []
problem_l = []

triangular_mesh = fk.TriangularMesh.from_msh_file('../simulations/inputs/simple_canal.msh') 

################################################################################
#
#Boundary conditions are statically defined in this example but they could have 
#been changed as well.
#

fluvial_flowrates = [fk.FluvialFlowRate(ref=1,
                                  flowrate=5.,
                                  x_flux_direction=1.0,
                                  y_flux_direction=0.0)]
fluvial_heights = [fk.FluvialHeight(ref=2, height=2.)]
slide = [fk.Slide(ref=3), fk.Slide(ref=4)]

################################################################################
#
# Resolution: 
#--------------------
#
#We loop over cases:

for C, NL in enumerate(cases):

    print(" ")
    print(" ")
    print("                         SOLVING CASE {}                 ".format(C))
    print(" ")
    print(" ")

    simutime_l.append(fk.SimuTime(final_time=1., time_iteration_max=100000))

    layer_l.append(fk.Layer(NL, triangular_mesh, topography=0.))

    primitives_l.append(fk.Primitive(triangular_mesh, layer_l[C], 
                                     free_surface=2., 
                                     QXinit=1.))

    problem_l.append(fk.Problem(simutime=simutime_l[C],
                                triangular_mesh=triangular_mesh,
                                layer=layer_l[C],
                                primitives=primitives_l[C], 
                                physical_parameters=PHY_PARAMS,
                                slides=slide,
                                fluvial_flowrates=fluvial_flowrates,
                                fluvial_heights=fluvial_heights))
    problem_l[C].solve()

################################################################################
#  
# Plot velocity profile: 
#-----------------------
#

cell = 233 #Middle domain
u = np.zeros((NL))   
z = np.zeros((NL))  

plt.rcParams["figure.figsize"] = [8, 6]
fig = plt.figure()
ax = fig.add_subplot(111)

colors = ['blue', 'red', 'green', 'purple']
markers = ['s', '*', 'o', 'v']

for C, NL in enumerate(cases):
    for L in range(NL):
        u[L] = problem_l[C].primitives.U[cell, L]
        z[L] = 0.5*(2.0/NL) + L*(2.0/NL)

    fig = ax.plot(u[0:NL], z[0:NL], color=colors[C], marker=markers[C], 
                  label='NL = {}'.format(NL))
    ax.set_title("Velocity profile in x = {}"
                  .format(triangular_mesh.triangulation.x[cell]))

ax.set_xlabel('U (m/s)')
ax.set_ylabel('z (m)')
plt.legend(loc=2)
plt.grid()
plt.show()

################################################################################
#
#.. note::
#   In this example only NL have been changed for each case but any ``Problem``
#   input  could been changed as well (mesh, intialization, simutime, etc...).
#
