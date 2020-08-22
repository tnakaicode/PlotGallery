"""
================================================================================
Raceway
================================================================================

In this example a raceway simulation with a paddle wheel is considered.
The geometry consist of a raceway with boundary condition being only walls.
Flow is maintained by a rotating wheel which provides kinetic energy to water.

"""

import os, sys
import argparse
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import freshkiss3d as fk
import freshkiss3d.geomalgo as ga
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Parameters:
#--------------------

#Numerical parameters:
FINAL_TIME = 2. #86400#1jour
NL = 10
WITH_TRACER = False
WITH_PARTICLES = False
NUM_PARAMS={'ipres':True,
            'space_second_order':False,
            'vertical_velocity_centered_scheme':False}

#Output parameters
NB_VTK = 10
#Paddle-wheel model parameters:
N_WHEELS = 2                     # Number of wheels: 6
CIRC_VELOCITY = 2.               # Circumferential velocity: 0.2, 0.4, 0.6, 0.8, 1.0
TORQUE = 10.0                    # <40

#Physical parameters:
ZB = 0.0                         # Topography
H0 = 0.5                         # Initial water height
ETA0 = 1.e-3                     # Dynamic water viscosity
ETA_TURB = 0.0                   # Eddy viscosity
FRICTION = 0.001                 # Friction coefficient
WALL_FRICTION = 1.               # Wall friction coefficient
VISCOSITY = ETA0*1e-3+ETA_TURB   # Cinematic viscosity coefficient
PHY_PARAMS={'friction_coeff':FRICTION,
            'horizontal_viscosity':VISCOSITY,
            'vertical_viscosity':VISCOSITY}

#Domain and geometry:
BOX_X_MAX = 2
BOX_X_MIN = 0
BOX_Y_MAX = -1
BOX_Y_MIN = -2
RADIUS = 0.6
A = ga.Point3D(-3.14, 2.3, 0.84)
B = ga.Point3D(-3.14, 0.6, 0.84)
SCALE_H = 5.

################################################################################
#
# Time loop:
#--------------------

simutime = fk.SimuTime(final_time=FINAL_TIME, second_order=False)

output_scheduler = fk.schedules(count=NB_VTK)
output_scheduler_lag = fk.schedules(count=NB_VTK)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/raceway.msh')
NC = triangular_mesh.NV
if WITH_PARTICLES: triangular_mesh.set_neighbours()

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

################################################################################
#
# Layers:
#--------------------

layer = fk.Layer(NL, triangular_mesh, topography=ZB)

################################################################################
#
# Primitives:
#--------------------

primitives = fk.Primitive(triangular_mesh, layer, height=H0)

################################################################################
#
# Tracer:
#--------------------

if WITH_TRACER:
    T_0 = np.zeros((NC, NL))
    for C in range(NC):
        for L in range(NL):
            x = triangular_mesh.triangulation.x[C]
            y = triangular_mesh.triangulation.y[C]
            if x < BOX_X_MAX and x > BOX_X_MIN and y > BOX_Y_MIN and y < BOX_Y_MAX:
                T_0[C, L] = 0.9

    tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit=T_0,
                         label='suspension', settling_velocity=0.0)]
else:
    tracers = []

################################################################################
#
# Particles:
#--------------------

if WITH_PARTICLES:
    positions = fk.generate_homogeneous_positions(triangular_mesh, layer, primitives, 3000)
    lagrangian = fk.Lagrangian(positions, triangular_mesh, layer, primitives,
                               scheduler=output_scheduler_lag)
else:
    lagrangian = None

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=101, horizontal_viscosity=VISCOSITY, wall_friction_coeff=WALL_FRICTION),
          fk.Slide(ref=102, horizontal_viscosity=VISCOSITY, wall_friction_coeff=WALL_FRICTION)]

################################################################################
#
# External effects:
#---------------------

angular_velocity = CIRC_VELOCITY/RADIUS
rotating = fk.Rotating(angles_number=N_WHEELS, angular_velocity=angular_velocity, phase=-np.pi)
wheels = [fk.Wheel(A, B, radius=RADIUS, magnitude=TORQUE, rotating=rotating),]
paddle_wheel_effect = fk.WheelEffect(wheels, triangular_mesh.vertices, layer)
external_effects = {"wheel": paddle_wheel_effect}

################################################################################
#
# Writter:
#----------------------
#

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=output_scheduler, scale_h=SCALE_H)

################################################################################
#
# Problem definition:
#--------------------

raceway = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     numerical_parameters=NUM_PARAMS,
                     physical_parameters=PHY_PARAMS,
                     external_effects=external_effects,
                     vtk_writer=vtk_writer,
                     tracers=tracers,
                     lagrangian=lagrangian)

################################################################################
#
# Problem solving:
#-----------------

raceway.solve()

################################################################################
#
# Post-processing with paraview:
#--------------------------------
#

os.system('python2.7 postpro_paraview/postpro_raceway.py -n {}'.format(NB_VTK))

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
#    With the command ``os.system('')`` paraview post-processing script ``postpro_raceway.py``
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
  plt.rcParams["figure.figsize"] = [15, 10]

  #plt.imshow(mpimg.imread('outputs/raceway_3.png'),interpolation="spline16")

  fig, axes = plt.subplots(nrows=3, ncols=2)

  for I, ax in zip(range(NB_VTK), axes.flat):
    ax.imshow(mpimg.imread('outputs/raceway_{}.png'.format(I)), interpolation="spline16")
    ax.set_title("time={:.2f} s".format(I*FINAL_TIME/NB_VTK))
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

  plt.suptitle('Velocity norm')
  plt.show()
