"""
================================================================================
Wind effect 
================================================================================

In this example ``WindEffect`` is illustrated. At the top of a cavity we set up
wind velocity and orientation. A circular flow is generated in the cavity.

"""

import os, sys
import matplotlib.pylab as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Wind effect:
#--------------------------------
#
#The wind friction shear stress on top layer can be expressed as:
#
#.. math:: \tau = \rho_{atm} C_d U_{wind}^2
#
#In freshkiss3d the friction coefficient Cd (empirical parameter) can be user-defined
#or chosen amongst a set of existing law (by default: Imberger & Patterson)
#
#- Imberger & Patterson (1984)
#
#   .. math:: 
#       \begin{cases}
#       C_d = 1,124.10^{-3}  \quad & \text{if} \quad U_{wind} \leq 4 m/s  \\
#       C_d = (0,94 + 0,041 U_{wind}) 10^{-3} \quad & \text{else}
#       \end{cases}
#
#- Stefan & Ford (1975)
#
#   .. math:: 
#       \begin{cases}
#       C_d = 0,5.10^{-3} \sqrt{U_{wind}} \quad & \text{if} \quad U_{wind} \leq 15 m/s  \\
#       C_d = 2,6.10^{-3} \quad & \text{else}
#       \end{cases}
#
#- Coantic (1978)
#
#   .. math:: 
#       C_d = (1 + 0.03 U_{wind}).10^{-3}

cases = ['Imberger_Patterson', 'Stefan_Ford', 'Coantic', 'Custom']

def custom_friction_law(v):
    return (0.75 + 0.067*v)*1.e-3

################################################################################
#
#In this example we compare all laws for a wind intensity of 20 m/s. Fluid
#dynamic viscosity is set to 1Pa.s and free surface to 2m.
#

################################################################################
#
# Mesh:
#--------------------
#

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
TG, vertex_labels, boundary_labels = fk.read_msh(dir_path + '/inputs/simple_canal_2.msh')
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)

x *= 10
y *= 10

triangular_mesh = fk.TriangularMesh(TG, vertex_labels, boundary_labels)

fk_plt.plot_mesh(triangular_mesh)

################################################################################
#
# Cases set-up:
#--------------------
#
#``WindEffect`` class need a velocity (in m/s) and orientation (in Azimuth degree).
#Both can be set to change over time. ``friction_law`` and ``friction_law_funct``
#are optional arguments.
#

NL = 20
PHY_PARAMS={'friction_coeff':1.,
            'horizontal_viscosity':0.01,
            'vertical_viscosity':0.01}
simutime_l = []
layer_l = []
primitives_l = []
wind_effect_l = []
external_effects_l = []
problem_l = []

for C, law in enumerate(cases):

    simutime_l.append(fk.SimuTime(final_time=5., time_iteration_max=10000,
                                  second_order=False))
    layer_l.append(fk.Layer(NL, triangular_mesh, topography=0.))
    primitives_l.append(fk.Primitive(triangular_mesh, layer_l[C], free_surface=2.0))

    if law == 'Custom':
        wind_effect_l.append(fk.WindEffect(velocity=[20, 20, 20, 20],
                                           orientation=[270., 270., 270., 270.],
                                           times=[0., 3., 4., 5.],
                                           friction_law_funct=custom_friction_law))
    else:
        wind_effect_l.append(fk.WindEffect(velocity=[20, 20, 20, 20],
                                           orientation=[270., 270., 270., 270.],
                                           times=[0., 3., 4., 5.],
                                           friction_law=law))

    external_effects_l.append({"wind": wind_effect_l[C]})

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#
# Problem:
#--------------------
#

for C, law in enumerate(cases):

    print(" ")
    print(" ")
    print("                          SOLVING CASE:                            ")
    print(" ")
    print(" ")

    problem_l.append(fk.Problem(simutime_l[C], triangular_mesh,
                                layer_l[C], primitives_l[C],
                                slides=slides,
                                physical_parameters=PHY_PARAMS,
                                external_effects=external_effects_l[C]))
    problem_l[C].solve()

################################################################################
#
# Plots:
#-----------------
#
#Vertical velocity is plotted for max layer case as well as x velocity profiles
#for each discretization.

plt.rcParams["figure.figsize"] = [12, 8]

plt.style.use('seaborn-white')
plt.rcParams['font.family'] = 'serif'
plt.rcParams['font.serif'] = 'Ubuntu'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 8
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 8
plt.rcParams['figure.titlesize'] = 12
plt.rcParams["axes.grid"] = True

fig = plt.figure()

colors = ['blue', 'purple', 'green', 'red']
markers = ['s', '*', 'o', 'v']

def plot_U_profile(cell, ax, problem_l,char):
    for C in range(len(cases)):
        u = np.zeros((len(cases), NL))
        z = np.zeros((len(cases), NL))
        for L in range(NL):
            u[C, L] = problem_l[C].primitives.U[cell,L]
            z[C, L] = 0.5*(2.0/NL) + L*(2.0/NL)
       
        ax.plot(u[C, :],z[C, :], color=colors[C], marker=markers[C], 
                       label="{}".format(cases[C]))
        
        ax.set_title("Velocity profile on node {}".format(char), fontstyle='italic')
    ax.legend(loc=4, shadow=True, title="Friction law")
    ax.set_xlabel('U (m/s)')
    ax.set_ylabel('z (m)')

#Velocity profile
cell = 84 
ax = plt.subplot2grid((3,4), (1,0), colspan=2, rowspan=2)
plot_U_profile(cell, ax, problem_l, 'A')

#Friction coeff comparisons
ax1 = plt.subplot2grid((3,4), (1,2), colspan=2, rowspan=2)
v_wind = np.linspace(0,30,100)

def Im(v): #'Imberger_Patterson'
    if v <= 4.:
        return 1.124*1.e-3
    else:
        return (0.94 + 0.041*v)*1.e-3

def St(v): #'Stefan_Ford'
    if v <= 15.:
        return 0.5*(np.sqrt(v))*1.e-3
    else:
        return 2.6*1.e-3

def Co(v): #'Coantic'
    return (1.+0.03*v)*1.e-3

C1 = np.zeros(len(v_wind))
C2 = np.zeros(len(v_wind))
C3 = np.zeros(len(v_wind))
C4 = np.zeros(len(v_wind))

for C in range(len(C1)):
    C1[C] = Im(v_wind[C])
    C2[C] = St(v_wind[C])
    C3[C] = Co(v_wind[C])
    C4[C] = custom_friction_law(v_wind[C])

ax1.plot(v_wind,C1,color=colors[0], label='Imberger_Patterson')
ax1.plot(v_wind,C2,color=colors[1], label='Stefan_Ford')
ax1.plot(v_wind,C3,color=colors[2], label='Coantic')
ax1.plot(v_wind,C4,color=colors[3], label='User defined')
ax1.set_title("Comparison of friction coefficients", fontstyle='italic')
ax1.legend(loc=4, shadow=True, title="Friction law")
ax1.set_xlabel('Wind velocity (m/s)')
ax1.set_ylabel('Cd (m)')

#Mesh and surface vertical velocity
tri = triangular_mesh.triangulation
ax2 = plt.subplot2grid((3,4), (0,0), colspan=4)
ax2.triplot(tri.x, tri.y, tri.trivtx, color='k', lw=0.5)
im = ax2.tricontourf(tri.x, tri.y, tri.trivtx, 
                     problem_l[len(cases)-1].primitives.W[:,int(NL/2)], 20,cmap=plt.cm.jet)
ax2.set_title('Vertical veloctiy on layer: {}'
              .format(int(NL/2)))
cbar = fig.colorbar(im, ax=ax2, aspect=8)
cbar.set_label('W (m/s)', y=1.1, labelpad=-25, rotation=0)
ax2.set_xlabel('x (m)')
ax2.set_ylabel('y (m)')
ofs=0.05

#cell
ax2.plot(tri.x[cell], tri.y[cell], marker='o', color='k', markersize=5)
ax2.text(tri.x[cell]+ofs, tri.y[cell]+ofs, "A", color='k', fontsize=15)

plt.tight_layout()
plt.show()

