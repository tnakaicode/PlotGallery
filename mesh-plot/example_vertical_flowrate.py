"""
================================================================================
Vertical flowrate
================================================================================

In this example ``VerticalFlowRate`` boundary condition is illustrated. Geometry
is defined so that every side is a wall. At the bottom we set two vertical flowrate
boundary conditions, the first being an inlet and the second an outlet.

"""
import os, sys
import matplotlib.pylab as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=1, time_iteration_max=10000,
                       second_order=True)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/simple_canal_2.msh')

fk_plt.plot_mesh(triangular_mesh)

################################################################################
#
# Layers:
#--------------------
#

NL = 4
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#
# Primitives:
#--------------------

primitives = fk.Primitive(triangular_mesh, layer, free_surface=.5)

################################################################################
#
# Tracer:
#--------------------
#

tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit=0.0, label='temperature')]

################################################################################
#
# Boundary conditions:
#---------------------
#
#``VerticalFlowRate`` boundary conditions consist of imposing vertical flowrate at the
#bottom on designated cells. In case of inlet you can also impose a Tracer value.
#If more than one cell is selected, imposed flowrate is shared based on cell area.
#As any other boundary condition, there can be as much ``VerticalFlowRate`` as needed
#as long as they are defined in a **list**.

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]
      
vertical_flowrate_in = fk.VerticalFlowRate(
    times=[0., 10, 20],
    flowrates=[0.1, 0.1, 0.1],
    cells=[97],
    tracers_inlet={'temperature':10.})

vertical_flowrate_out = fk.VerticalFlowRate(
    times=[0., 10, 20],
    flowrates=[-0.1, -0.1, -0.1],
    cells=[94],
    tracers_inlet={'temperature':10.})

vertical_flowrates = [vertical_flowrate_in, vertical_flowrate_out]

NUM_PARAMS={'ipres':True,
            'flux_type':1,
            'implicit_exchanges':True}

################################################################################
#
# Writter: 
#----------------------
#

NB_VTK = 10

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=NB_VTK),
                          scale_h=2.)

################################################################################
#
# Problem definition:
#--------------------

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     tracers=tracers,
                     slides=slides, 
                     vertical_flowrates=vertical_flowrates,
                     numerical_parameters=NUM_PARAMS,
                     vtk_writer=vtk_writer)

################################################################################
#
# Problem solving:
#-----------------

problem.solve()

################################################################################
#
# Plots:
#-----------------
#
#Velocity norm is plotted for each layer:
#

vertex_labels = triangular_mesh.vertex_labels
boundary_labels = triangular_mesh.boundary_labels 
x = np.asarray(triangular_mesh.triangulation.x)
y = np.asarray(triangular_mesh.triangulation.y)
trivtx = np.asarray(triangular_mesh.triangulation.trivtx)

NC = len(x)
index = range(NL)
velocity = np.zeros((NC))

fig, axes = plt.subplots(nrows=len(index)) #, ncols=2)
v = np.linspace(-.1, .1, 10, endpoint=True)

for L, ax in zip(reversed(index), axes.flat):
    lab = 'L={}'.format(L)
    ax.triplot(x, y, trivtx, color='k', lw=0.5)
    # VELOCITY: 
    for C in range(NC):
        velocity[C] = problem.primitives.W[C,L]
    #    velocity[C] = np.sqrt( problem.primitives.U[C,L]**2 + \
    #                           problem.primitives.V[C,L]**2 + \
    #                           problem.primitives.W[C,L]**2 )
    im = ax.tricontourf(x, y, trivtx, velocity[:], v, cmap=plt.cm.bwr)
    cbar = fig.colorbar(im, ax=ax, aspect=8, ticks=v)
    cbar.set_label(lab, rotation=90)

axes[0].set_title('Vertical veloctiy (W)'.format(L))

for L in range(len(index)-1): plt.setp(axes[L].get_xticklabels(), visible=False)

for a, b, label in zip(x, y, vertex_labels):
    if a < 0.45 and a > 0.35 and b < 0.3 and b > 0.2:
        axes[len(index)-1].plot(a, b, marker='o', color='k', markersize=5)
    if a < 1.8 and a > 1.7 and b < 0.3 and b > 0.2:
        axes[len(index)-1].plot(a, b, marker='o', color='k', markersize=5)
axes[len(index)-1].annotate('VerticalFlowRate in', xy=(0.37, 0.25), xytext=(0.2, -0.3), 
        arrowprops=dict(facecolor='black', width=0.2, headwidth=5, shrink=0.1))
axes[len(index)-1].annotate('VerticalFlowRate out', xy=(1.73, 0.25), xytext=(1.3, -0.3), 
        arrowprops=dict(facecolor='black', width=0.2, headwidth=5, shrink=0.1))

plt.show()
