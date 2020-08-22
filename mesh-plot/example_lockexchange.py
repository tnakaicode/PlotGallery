"""
================================================================================
Lock exchange
================================================================================

In this example the simulation of a lock exchange is carried out with the 
Navier-Stokes-Fourier system. Initially high density water is placed on the left
side of the domain and low density water on the right side. 
You can switch to the Boussinesq approximation variable density model by setting 
'variable_density_model' to 'boussinesq'.

"""

import os, sys
import argparse
import numpy as np
import matplotlib.pylab as plt
import matplotlib.image as mpimg
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt
from freshkiss3d.core.state_laws import *

os.system('rm -r outputs')

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Parameters:
#----------------------
#

FINAL_TIME = 500.
NL = 8
GATE_POSITION = 50.
TIME_SECOND_ORDER = True
NUM_PARAMS={'ipres':True,
            'space_second_order':False,
            'flux_type':2,
            'implicit_exchanges':True,
            'implicit_vertical_viscosity':True}

PHY_PARAMS={'friction_law':'Navier',
            'friction_coeff':0.0,
            'horizontal_viscosity':0.0,
            'vertical_viscosity':0.0,
            'variable_density':True,
            'variable_density_model': 'ns-fourier'} #'boussinesq' or 'ns-fourier'

################################################################################
#
# Time loop:
#--------------------
#
#Second order time numerical scheme is disable by default for quicker execution.

simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=100000,
                       second_order=TIME_SECOND_ORDER)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/floodgate.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh)


################################################################################
#  
# Layers: 
#--------------------

layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#  
# Boundary conditions: 
#---------------------

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#
# Tracer:
#--------------------
#

def T_0(x, y):
    if x < GATE_POSITION:
        value = 10.
    else:
        value = 50.
    return value

def Rho_0(x, y):
    if x < GATE_POSITION:
        T = 10
        value = Rho_sea_water(T, 0.)
    else:
        T = 50.
        value = Rho_sea_water(T, 0.)
    return value

if PHY_PARAMS['variable_density_model'] == 'boussinesq':
    primitives = fk.Primitive(triangular_mesh, layer, free_surface=2.0)
    tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit_funct=T_0,
                         label='temperature',
                         horizontal_diffusivity=0.0,
                         vertical_diffusivity=0.0)]

elif PHY_PARAMS['variable_density_model'] == 'ns-fourier':
    primitives = fk.Primitive(triangular_mesh, layer, free_surface=2.0, 
                              Rhoinit_funct=Rho_0)
    tracers = []

################################################################################
#
# Custom functions: 
#----------------------
#

def compute_volume(problem):
    HL = problem.primitives.HL
    NC = HL.shape[0]
    NL = HL.shape[1]
    unity = np.ones((NC,NL))
    cell_area = problem.finite_volume_mesh.cells.area
    volume = fk.compute_integral(cell_area, HL, unity)
    print("Total volume = ", volume, "m3")

def compute_mass(problem):
    HL = problem.primitives.HL
    Rho = problem.primitives.Rho
    cell_area = problem.finite_volume_mesh.cells.area
    mass = fk.compute_integral(cell_area, HL, Rho)
    print("Total mass = ", mass, "kg")

custom_scheduler = fk.schedules(count=5)
custom_functions = {'volume':compute_volume, 'mass':compute_mass}

################################################################################
#
# Writter: 
#----------------------
#

NB_VTK = 10

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=NB_VTK),
                          scale_h=20.)

################################################################################
#  
# Problem definition: 
#--------------------

problem = fk.Problem(simutime, triangular_mesh,
                     layer, primitives,
                     slides=slides,
                     tracers=tracers, 
                     numerical_parameters=NUM_PARAMS,
                     physical_parameters=PHY_PARAMS,
                     vtk_writer=vtk_writer,
                     custom_funct=custom_functions,
                     custom_funct_scheduler=custom_scheduler)

################################################################################
#  
# Problem solving: 
#-----------------

problem.solve()


################################################################################
#
# Post-processing with paraview:
#--------------------------------
#  

os.system('python2.7 postpro_paraview/postpro_lockexchange.py -n {}'.format(NB_VTK))

################################################################################
#
#.. note::
#    To be able to use paraview post-processing scripts you need to install python2.7
#    (outside conda envs. fk) and add the following lines to your ``.bashrc``:
#
#    .. code-block:: bash
#
#       export PYTHONPATH=$PYTHONPATH:/usr/lib/python2.7/site-packages
#       export PYTHONPATH=$PYTHONPATH:/usr/lib/paraview/site-packages
#
#    With the command ``os.system('')`` paraview post-processing script ``postpro_settling.py``
#    located in the ``/paraview`` subfolder is called.
#    This script creates a ``.png`` file that can then be retrieved and manipulated with matplotlib.

if not args.nographics:
  plt.style.use('seaborn-white')
  plt.rcParams['font.family'] = 'serif'
  plt.rcParams['font.size'] = 14
  plt.rcParams['axes.labelsize'] = 12
  plt.rcParams['axes.labelweight'] = 'bold'
  plt.rcParams['axes.titlesize'] = 14
  plt.rcParams['xtick.labelsize'] = 10
  plt.rcParams['ytick.labelsize'] = 10
  plt.rcParams['legend.fontsize'] = 12
  plt.rcParams['figure.titlesize'] = 16
  plt.rcParams["axes.grid"] = False
  plt.rcParams["figure.figsize"] = [10, 8]

  fig, axes = plt.subplots(nrows=3, ncols=2)

  for I, ax in zip(range(NB_VTK), axes.flat):
    ax.imshow(mpimg.imread('outputs/lockexchange_{}.png'.format(I)), interpolation="spline16")
    ax.set_title("time={:.2f} s".format(I*FINAL_TIME/NB_VTK))
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

  plt.suptitle('Density in (x,z) plane')
  plt.show()
