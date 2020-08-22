"""
================================================================================
Restart
================================================================================

In this tutorial, the restart functionnality of Freshkiss3D is explained.

"""
import os
import matplotlib.pylab as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')
#sphinx_gallery_thumbnail_number = 4

################################################################################
#
# Restart scheduler: 
#--------------------
#
#To enable the restart, you have to set a restart ``Scheduler`` and pass it to the 
#``Problem`` class. Here we set the restart scheduler to time and set it to 1,2 and 3s.
#At the first time set simulation will stop and create a back up save file. Saved data ara stored
#inside a ``restart_data.h5`` file that allow to perform a restart of the simulation
#from the time it stopped. 
# 
restart_times = [1., 2., 3.]
restart_scheduler = fk.schedules(times=restart_times)

################################################################################
#
#.. note::
#   Restart can be performed several times in the same simulation. In our case, 
#   simulation time is splitted in 4 sections, and 3 iterative restarts are performed.
#

################################################################################
#
# Case set-up: 
#--------------------
#
simutime = fk.SimuTime(final_time=4., time_iteration_max=20000, second_order=True)
create_figure_scheduler = fk.schedules(times=[0., 1., 2., 3., 4., 5.])
triangular_mesh = fk.TriangularMesh.from_msh_file('../simulations/inputs/square2.mesh')
layer = fk.Layer(1, triangular_mesh, topography=0.)

def H_0(x, y):
    h = 2.4*(1.0 + np.exp(-0.25*((x-10.05)**2+(y-10.05)**2)))
    return h

primitives = fk.Primitive(triangular_mesh, layer, height_funct=H_0)
tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit=1.0)]
slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]
vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=10), scale_h=1.)

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     numerical_parameters={'space_second_order':True},
                     tracers=tracers,
                     vtk_writer=vtk_writer,
                     restart_scheduler=restart_scheduler,
                     custom_funct={'plot':fk_plt.plot_freesurface_3d},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#
# Solving first part: 
#--------------------
#
#The restart sheduler first time being set to 1s, the ``solve()`` function will 
#stop and save data at time=1s.
#
problem.solve()
plt.show()

################################################################################
#
# Restart: 
#--------------------
#
#Simulation is restarted from ``restart_data.h5`` file with the ``restart()`` function.
#
for I in range(len(restart_times)):
    problem.restart(iteration=I)
    plt.show()

################################################################################
#
#.. note:: 
#   Simulation can be restarted from any location using the ``restart`` function of 
#   the ``Problem`` class as long as the case set-up is not changed and the ``restart_data.h5`` 
#   file exists. 
#

os.system('rm restart_data.h5')
