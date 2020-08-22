"""
=====================
Height source
=====================

This case is showing the ability of freshkiss3d to apply
source terms on water height to simulate rain or infiltration effects.

"""
import os, sys
import argparse
import numpy as np
import random as rd
import matplotlib.pylab as plt
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 3

################################################################################
#
# Time loop: 
#--------------------

FINAL_TIME = 10.
simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=20000, second_order=True)

create_figure_scheduler = fk.schedules(times=[0., 4., 8.])

################################################################################
#  
# Mesh: 
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/square2.mesh')   

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh)

################################################################################
#  
# Layers: 
#--------------------

NL = 2
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#  
# Primitives: 
#--------------------
#
#Initial height is set to :math:`10 cm`.
 
primitives = fk.Primitive(triangular_mesh, layer, height=0.1)

################################################################################
#  
# Height source term: 
#--------------------
#
#``ExternalEffects`` objects are called in ``problem.solve()`` at each time step. In
#this example external effects are ``HeightSource``.
#There can be as much external effects as needed as long as they are stored in a
#dictionary type. 
#
#Let us consider two cases:
#
# * In the first case we define continuous height source over time which means that the source given is either the rate of infiltration (if negative) or the rain intensity (if positive) both in m/s. 
# * In the second case we define sparse height source over time to simulate water droplets falling on free surface at specified times. Water height source unit is set to m. 
#
#.. note::
#   Note that in both cases (continuous or sparse over time), the source can be either
#   homogeneous or heterogeneous in space i.e. user can set either a constant set of sources 
#   with the ``sources`` parameter or a function (or set of function) of x, y with
#   the ``sources_funct`` parameter.
#

CASE = 2

################################################################################
#  
#Case 1: In this case rain intensity is set to :math:`2 cm/s` and infiltration rate 
#to :math:`1 cm/s`. With an initial height of :math:`10 cm` and a final time of 
#:math:`10 s`, height should double by the end of the simulation. In this case
#the source is continuous in time and homogeneous in space.
#
if CASE == 1:
    rain = fk.HeightSource(
        times=[1., FINAL_TIME],
        sources=[0.02, 0.02],
        source_unit='m/s')

    infiltration = fk.HeightSource(
        times=[1., FINAL_TIME],
        sources=[-0.01, -0.01],
        source_unit='m/s')

    external_effects = {"rain": rain, "infiltration": infiltration}

################################################################################
#  
#Case 2: water droplets are defined by a gaussian function with random position and 
#random time of fall. In this case, the source is sparse in time and heterogeneous
#in space.
#
if CASE == 2:
    TG = triangular_mesh.triangulation
    x_min = min(TG.x); x_max = max(TG.x)
    y_min = min(TG.y); y_max = max(TG.y)

    def function_generator():
        def water_drop_source(x, y, x_0=rd.uniform(x_min, x_max),
                                    y_0=rd.uniform(y_min, y_max)):
            return .003*np.exp(-10.*((x-x_0)**2+(y-y_0)**2))
        return water_drop_source

    #randomized water drops:
    drop_number = 200
    water_drop_times = np.sort(np.array([rd.uniform(0.,FINAL_TIME) for t in range(drop_number)]))
    water_drop_functions = [function_generator() for t in range(drop_number)]

    rain_sparse = fk.HeightSource(
        times=water_drop_times,
        sources_funct=water_drop_functions,
        source_unit='m')

    external_effects = {"sparse rain": rain_sparse}

################################################################################
#
# Boundary conditions: 
#---------------------

slides = [fk.Slide(ref=r) for r in [1,2,3,4]]

################################################################################
#
# Writter: 
#---------------------- 
#

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=10),
                          scale_h=20.)

################################################################################
#  
# Problem definition: 
#--------------------

problem = fk.Problem(simutime, triangular_mesh, 
                     layer, primitives, 
                     slides=slides,
                     external_effects=external_effects,
                     vtk_writer=vtk_writer,
                     custom_funct={'plot':fk_plt.plot_freesurface_3d},
                     custom_funct_scheduler=create_figure_scheduler)

################################################################################
#  
# Problem solving: 
#-----------------

problem.solve()

if not args.nographics:
  plt.show()
