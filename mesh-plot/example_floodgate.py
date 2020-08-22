"""
================================================================================
Floodgate
================================================================================

In this example the simulation of a flood gate opening is carried out using
the Navier-Stokes with variable density model and the Boussinesq approximation.
Initially heavy water is placed on the left side of the floodgate and light water
on the right side. 

For density computation the International Equation of state of Seawater is used.
It gives density as a function of temperature and salinity which are solved with 
convetion-diffusion tracer equations. The floodgate opening is simulation several 
times thanks to a tracer source term defined on the left side of the gate.

"""
import os, sys
import argparse
import matplotlib.pylab as plt
import matplotlib.image as mpimg
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

os.system('rm -r outputs')

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 4

################################################################################
#
# Parameters:
#----------------------
#

FINAL_TIME = 400.
NL = 8
TIME_SECOND_ORDER = False
NUM_PARAMS={'ipres':True,
            'space_second_order':False,
            'flux_type':1,
            'implicit_vertical_viscosity':True}

PHY_PARAMS={'friction_law':'Navier',
            'friction_coeff':0.001,
            'horizontal_viscosity':5e-4,
            'vertical_viscosity':5e-4,
            'variable_density':True}

################################################################################
#
# Time loop:
#--------------------
#
#Second order time numerical scheme is disable by default for quicker execution.
#

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
# Topography:
#--------------------
#
#Topography is flat and constant (1m) on the left side and is defined as a ramp on the
#right side so that bottom height equals zero on boundary.
#

GATE_POSITION = 20.
X_B = 60.
def topo(x, y):
    if x < GATE_POSITION:
        topo = 1.0
    elif x > X_B:
        topo = 0.0
    else:
        topo = -(1.0/(X_B-GATE_POSITION))*(x - X_B)
    return topo

################################################################################
#  
# Layers: 
#--------------------

layer = fk.Layer(NL, triangular_mesh, topography_funct=topo)

################################################################################
#  
# Primitives: 
#--------------------
#
#We initialize free surface at 2m. Velocity is set to zero by default.
#

primitives = fk.Primitive(triangular_mesh, layer, free_surface=2.0)

################################################################################
#  
# Boundary conditions: 
#---------------------
#

slides = [fk.Slide(ref=r) for r in [1, 2, 3, 4]]

################################################################################
#  
# Tracers: 
#--------------------
#
#Two tracers are defined. One for the salinity S and the second for the 
#temperature T. We use the following functions to define initial tracer values 
#on each side of the floodgate:
#

def S_0(x, y):
    if x < GATE_POSITION:
        value = 35.
    else:
        value = 0.
    return value

def T_0(x, y):
    if x < GATE_POSITION:
        value = 10.
    else:
        value = 4.
    return value

tracers = [fk.Tracer(triangular_mesh, layer, primitives, Tinit_funct=T_0,
                     label='temperature',
                     horizontal_diffusivity=1.777e-9,
                     vertical_diffusivity=1.777e-9),
           fk.Tracer(triangular_mesh, layer, primitives, Tinit_funct=S_0,
                     label='salinity',
                     horizontal_diffusivity=1.e-10,
                     vertical_diffusivity=1.e-10)]

################################################################################
#
# External effects (tracer source terms):
#----------------------------------------
#
#Floodgate refills and re-opens at time 50s and 100s. Tracer source term is defined 
#on temperature and on salinity.
#

def T_source(x, *args):
    if x < GATE_POSITION:
        value = 0.01
    else:
        value = 0.
    return value

if not args.nographics:
  fk_plt.plot_init_1d_slice(triangular_mesh, surf=2.0, topo_xy=topo, 
                            primitive_xy=T_source, title='Temperature source term')

def S_source(x, *args):
    # Salinity inside floodgate is 35 kg/m3
    if x < GATE_POSITION:
        value = 30.
    else:
        value = 0.
    return value

if not args.nographics:
  fk_plt.plot_init_1d_slice(triangular_mesh, surf=2.0, topo_xy=topo, 
                            primitive_xy=S_source, title='Salinity source term')

################################################################################
#
#The parameter ``source_unit='[T]'`` means that the tracer unit is used for source
#term. In the case of the temperature, source term is defined in °C. User can also use
#``source_unit='[T]/s'`` in which case source is continuous in time, i.e. for temperature
#the source term is a rate of evolution in °C/s.
#

temperature_source = fk.TracerSource(
    times=[50., 100.],
    sources_funct=T_source,
    source_unit='[T]/s',
    tracer_label='temperature')

salinity_source = fk.TracerSource(
    times=[50., 100.],
    sources_funct=S_source,
    source_unit='[T]',
    tracer_label='salinity')

external_effects = {"continuous": temperature_source, "sparse": salinity_source}

################################################################################
#
# Writter: 
#---------------------- 
#

NB_VTK = 10

vtk_writer = fk.VTKWriter(triangular_mesh, scheduler=fk.schedules(count=NB_VTK),
                          scale_h=5.)

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
                     external_effects=external_effects,
                     vtk_writer=vtk_writer)

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

os.system('python2.7 postpro_paraview/postpro_floodgate.py -n {}'.format(NB_VTK))

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
#    With the command ``os.system('')`` paraview post-processing script ``postpro_floodgate.py``
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
  plt.rcParams["figure.figsize"]=[6, 10]

  fig = plt.figure()

  ax1 = fig.add_subplot(211)
  im1 = mpimg.imread('outputs/floodgate_3D.png')
  ax1.imshow(im1, interpolation="spline16")
  ax1.set_title("Salinity at time={} s".format(FINAL_TIME))
  plt.setp(ax1.get_xticklabels(), visible=False)
  plt.setp(ax1.get_yticklabels(), visible=False)

  ax2 = fig.add_subplot(212)
  im2 = mpimg.imread('outputs/floodgate_side.png')
  ax2.imshow(im2, interpolation="spline16")
  ax2.set_title("Salinity in (x,z) plane at time={} s".format(FINAL_TIME))
  plt.setp(ax2.get_xticklabels(), visible=False)   
  plt.setp(ax2.get_yticklabels(), visible=False)

  plt.show()
