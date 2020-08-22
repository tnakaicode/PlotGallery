"""
================================================================================
Post-processing with Matplotlib
================================================================================

In this example we show how to use matplotlib as a pre and post-treatment tool to easily plot 
meshes and solutions. River example is used as a basis for this tutorial. 
For advanced visualizations it is strongly advised to use a post-treatment software like paraview or mayavi. 

"""

import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
import freshkiss3d as fk

################################################################################
#
# Quick case set up: 
#--------------------
#

simutime = fk.SimuTime(final_time=1500., time_iteration_max=100000)

triangular_mesh = fk.TriangularMesh.from_msh_file('../simulations/inputs/river.msh')

NL = 8
layer = fk.Layer(NL, triangular_mesh, topography=0.)

primitives = fk.Primitive(triangular_mesh, layer, height=1.0)

flowrate = fk.TimeDependentFlowRate(times=[0.0, 1000.0, 10000],
                                    flowrates=[0.0, 10.0, 10.0])

fluvial_flowrates = [fk.FluvialFlowRate(ref=2,
                                  time_dependent_flowrate=flowrate,
                                  x_flux_direction=1.0,
                                  y_flux_direction=0.0)]

slides = [fk.Slide(ref=1)]
fluvial_heights = [fk.FluvialHeight(ref=3, height=1.)]


################################################################################
#  
# Plot boundary conditions on mesh: 
#-----------------------------------
#
#To check boundary labels:
#
colors = {0:'blue', 1:'red', 2:'green', 3:'purple'}

fig = plt.figure()
ax = fig.add_subplot(111)
ax.triplot(triangular_mesh.triangulation.x, 
           triangular_mesh.triangulation.y,
           triangular_mesh.triangulation.trivtx)

# Plot edges.
for B in range(triangular_mesh.boundary_edges.size):
    i0 = triangular_mesh.boundary_edges.vertices[B, 0]
    i1 = triangular_mesh.boundary_edges.vertices[B, 1]
    x0,y0 = triangular_mesh.triangulation.x[i0], triangular_mesh.triangulation.y[i0]
    x1,y1 = triangular_mesh.triangulation.x[i1], triangular_mesh.triangulation.y[i1]
    ax.plot([x0, x1], [y0, y1], color=colors[triangular_mesh.boundary_edges.label[B]], linewidth=2.)
    offset = 0.04
    x_edge = 0.5*( x0 + x1) + offset
    y_edge = 0.5*( y0 + y1) + offset
    ax.text(x_edge, y_edge, triangular_mesh.boundary_edges.label[B], 
            color= colors[triangular_mesh.boundary_edges.label[B]],fontsize=10)

plt.grid()
plt.axis('scaled')
plt.show()

################################################################################
#  
# Problem solving: 
#--------------------
#

river = fk.Problem(simutime, triangular_mesh, layer, primitives,
                   slides=slides,
                   fluvial_flowrates=fluvial_flowrates,
                   fluvial_heights=fluvial_heights)

river.solve()

################################################################################
#  
# Basic plots of velocity components: 
#--------------------------------------
#
#First velocity components are plotted on the middle layer (see *LAYER_IDX*).

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
im1 = ax1.tricontourf(x, y, trivtx, river.primitives.U[:, LAYER_IDX], 30)
fig.colorbar(im1, ax=ax1)
ax1.set_title("Velocity x component on layer {}".format(LAYER_IDX))

# Subplot 2: y velocity
ax2 = fig.add_subplot(122)
ax2.triplot(x, y, trivtx, color='k', lw=0.5)
im2 = ax2.tricontourf(x, y, trivtx, river.primitives.V[:, LAYER_IDX], 30)
fig.colorbar(im2, ax=ax2)
ax2.set_title("Velocity y component on layer {}".format(LAYER_IDX))

plt.show()

################################################################################
#  
# Quivers plot: 
#------------------

plt.rcParams["figure.figsize"] = [6, 6]
fig = plt.figure()
ax1 = fig.add_subplot(111)
ax1.quiver(triang.x, triang.y, river.primitives.U[:, LAYER_IDX], 
                               river.primitives.V[:, LAYER_IDX])
ax1.set_title("Quivers on layer {}".format(LAYER_IDX))

plt.show()

################################################################################
#  
# Streamlines plot: 
#------------------

plt.rcParams["figure.figsize"] = [8, 6]
fig = plt.figure()
ax1 = fig.add_subplot(111)
xi, yi = np.meshgrid(np.linspace(0, 2000, 500), 
                     np.linspace(0, 2000, 500))
U_interp = mtri.LinearTriInterpolator(triang,river.primitives.U[:, LAYER_IDX])
V_interp = mtri.LinearTriInterpolator(triang,river.primitives.V[:, LAYER_IDX])
U_i = U_interp(xi, yi)
V_i = V_interp(xi, yi)
speed=np.sqrt(U_i**2+V_i**2)       
ax1.set_xlim(0, 2000) 
ax1.set_ylim(0, 2000)
strm = ax1.streamplot(xi, yi, U_i, V_i, density=(2, 2), color=speed, linewidth=2*speed/speed.max())
fig.colorbar(strm.lines)
ax1.set_title("Velocity & Streamlines on layer {}".format(LAYER_IDX))

plt.show()

