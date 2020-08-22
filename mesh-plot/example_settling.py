"""
================================================================================
Settling
================================================================================

In this example a static cavity is filled with a bulk suspensions. Settling
occurs due to the density difference between particles and liquid and a
stratification process is visible at the bottom of the domain.

"""

import os, sys
import argparse
import matplotlib.pylab as plt
import matplotlib.image as mpimg
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

#sphinx_gallery_thumbnail_number = 2

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

################################################################################
#
# Settling velocity:
#--------------------
#
#In freshkiss settling velocity is computed as follows:
#
#.. math::
#   \begin{cases}
#   w_s(T) = -K \left( 1- T \right)^3 \\
#   K=\frac{2a^2 \Delta \rho g}{9 \eta_0}
#   \end{cases}
#
#.. math:: a, \Delta \rho, \eta_0 \quad \text{being particle radius, density difference and bulk viscosity respectively}

################################################################################
#
#To activate setling model you need to provide the constant K (namely ``settling_velocity``
#in freshkiss3d) to the ``fk.Tracer class``.

SETTLING_VELOCITY = 0.8

PHY_PARAMS={'variable_density':True,
            'rho_suspension':1001}

################################################################################
#
#.. note::
#   Freshkiss uses Rusanov explicit scheme to solve vertical exchanges when settling
#   model is active. This scheme is stable under a CFL condition. Hence you might need
#   to tweak the number of layers based on settling velocity to satisfy this condition.
#   If CFL condition is not statisfied, freshkiss3d will automatically stop
#   the computation and raise a value error.

################################################################################
#
# Time loop:
#--------------------

FINAL_TIME = 6.
simutime = fk.SimuTime(final_time=FINAL_TIME, time_iteration_max=200000, second_order=False)

################################################################################
#
# Mesh:
#--------------------

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/simple_canal_2.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

################################################################################
#
# Layers:
#--------------------

NL = 25
layer = fk.Layer(NL, triangular_mesh, topography=0.)

################################################################################
#
# Primitives:
#--------------------
#
#Initial height is defined thanks to a user defined function.

primitives = fk.Primitive(triangular_mesh, layer,
                          height=2.,
                          Uinit=0.,
                          Vinit=0.)

################################################################################
#
# Tracer:
#--------------------
#

NC = triangular_mesh.NV

T_0 = np.zeros((NC, NL))
Lm = int(6*NL/10)
for C in range(NC):
    for L in range(NL):
        T_0[C, L] = 0.1 + 0.65*np.exp(-(L-Lm)**2/20.)

tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit=T_0,
                     label='suspension',
                     horizontal_diffusivity=0.0,
                     vertical_diffusivity=0.0,
                     settling_velocity=SETTLING_VELOCITY)]

################################################################################
#
# Boundary conditions:
#---------------------

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#
# Wind forcing:
#---------------------

WIND_FORCING = False
WIND_VELOCITY = 200

wind_effect = fk.WindEffect(velocity=[WIND_VELOCITY, WIND_VELOCITY],
                            orientation=[270., 270.],
                            times=[0., 10.])
if WIND_FORCING:
    external_effects = {"wind": wind_effect}
    PHY_PARAMS.update({'friction_coeff':1.,
                       'horizontal_viscosity':0.1,
                       'vertical_viscosity':0.1})
else:
    external_effects = None

################################################################################
#
# Writter:
#---------------------- 
#

NB_VTK = 6
vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=NB_VTK),
                          scale_h=1.)

txt_writer = fk.TXTWriter([84], scheduler=fk.schedules(count=NB_VTK))

################################################################################
#
# Problem definition:
#--------------------

NUM_PARAMS={'space_second_order':False,
            'implicit_exchanges':False}

problem = fk.Problem(simutime, triangular_mesh, layer, primitives,
                     slides=slides,
                     tracers=tracers, 
                     external_effects=external_effects, 
                     numerical_parameters=NUM_PARAMS,
                     physical_parameters=PHY_PARAMS,
                     vtk_writer=vtk_writer,
                     txt_writer=txt_writer)

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

os.system('python2.7 postpro_paraview/postpro_settling.py -n {}'.format(NB_VTK))

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
    ax.imshow(mpimg.imread('outputs/settling_{}.png'.format(I)), interpolation="spline16")
    ax.set_title("time={:.2f} s".format(I*FINAL_TIME/NB_VTK))
    plt.setp(ax.get_xticklabels(), visible=False)
    plt.setp(ax.get_yticklabels(), visible=False)

  plt.suptitle('Tracer in (x,z) plane')
  plt.show()

################################################################################
#
# Post-processing with matplotlib:
#---------------------------------
#

if not args.nographics:

  plt.rcParams["axes.grid"] = True
  plt.rcParams["figure.figsize"] = [10, 8]
  fig = plt.figure()

  ax = fig.add_subplot(111)

  txt_reader = fk.TXTReader([84], NL, N_tracers=1)
  TIME, z, H, U, V, W, Rho, Tracers = txt_reader.read_solution()

  #Warning: inverted shape of T in tracers list
  #print(Rho.shape)
  #print(Tracers[0].T.shape)

  ax.plot(z[0, :, 0], Tracers[0].T[0, :, 0], color='r', label='t = {} s'.format(0))

  for K in range(1, NB_VTK-1):   
    ax.plot(z[0, :, K], Tracers[0].T[K, :, 0], label='t = {} s'.format(K))

  ax.grid(True)
  ax.legend(loc=1, shadow=True, title="$Time$")
  ax.set_title('Volume fraction evolution')
  ax.set_xlabel('z (m)')
  ax.set_ylabel('Particle volume fraction')

  plt.show()

