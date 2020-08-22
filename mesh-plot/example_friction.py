"""
================================================================================
Friction
================================================================================

In this example a fluvial flow in a canal with friction is illustrated.

"""
import os, sys
import argparse
import matplotlib.pylab as plt
import numpy as np
import freshkiss3d as fk
import freshkiss3d.extra.plots as fk_plt

parser = argparse.ArgumentParser()
parser.add_argument('--nographics', action='store_true')
args = parser.parse_args()

#sphinx_gallery_thumbnail_number = 2

################################################################################
#
# Friction:
#--------------------------------
#
#Shear stress on bottom section can be expressed as:
#
#.. math:: (\boldsymbol{\Sigma}. \mathbf{n}_b).  \mathbf{t}_b = - \kappa_b(h,\mathbf{u}) \mathbf{u} .\mathbf{t}_b
#
#In freshkiss3d, Friction is defined via the ``friction_law`` and ``friction_coef`` keys of the 
#``physical_parameters`` dictionary. the friction
#coefficient :math:`\kappa_b(h,\mathbf{u})` can be chosen amongst the following laws:
#
#- Navier (``friction_law:'Navier'``):
#
#   .. math::
#       \kappa_b(h,{\bf u}) = \kappa
#
#- Chézy (``friction_law:'Chezy'``):
#
#   .. math::
#       \kappa_b(h,\mathbf{u}) = \dfrac{g}{C_h^2}.|\mathbf{u}|
#
#- Strikler (``friction_law:'Strickler'``):
#
#   .. math::
#       \kappa_b(h,\mathbf{u}) = \dfrac{g}{S_t^2} \left( \dfrac{|\mathbf{u}|}{h^{1/3}} \right)
#
#- Manning (``friction_law:'Manning'``):
#
#   .. math::
#       \kappa_b(h,\mathbf{u}) = g M_a^2 \left( \dfrac{|\mathbf{u}|}{h^{1/3}} \right)
#
#In each case you have to provide the friction coefficient (``friction_coeff``)
#corresponding to the chosen law (i.e. :math:`\kappa`, :math:`C_h`, :math:`S_t`, :math:`M_a`).
#

################################################################################
#
#.. warning::
#   Only the Navier formulation is valid for multilayer system as Chézy,
#   Strikler and Manning are empiricaly scaled on monolayer St Venant system.
#

################################################################################
#
# Cases set-up:
#--------------------
#
#In this example we compare all laws with equivalent coefficient.
#

FINAL_TIME = 40.

G = 9.81
H0 = 2.0
Q0 = 5.0
Cd = 0.015

Na = Cd
Ch = np.sqrt(G*Q0/(Cd*H0))
St = np.sqrt(G*Q0/(Cd*pow(H0,4.0/3.0)))
Ma = np.sqrt(Cd*pow(H0,4.0/3.0)/(G*Q0))

FRICTION_PARAMS = {'Navier':Na, 'Chezy':Ch,'Strickler':St, 'Manning':Ma}
NL              = {'Navier':6, 'Chezy':1, 'Strickler':1,  'Manning':1}

#print(FRICTION_PARAMS)

NUMERICAL_PARAMS = {'implicit_vertical_viscosity':True}

simutime_l = []
layer_l = []
primitives_l = []
problem_l = []

dir_path = os.path.abspath(os.path.dirname(sys.argv[0]))
triangular_mesh = fk.TriangularMesh.from_msh_file(dir_path + '/inputs/simple_canal.msh')

if not args.nographics:
  fk_plt.plot_mesh(triangular_mesh, plot_labels=False)

fluvial_flowrates = [fk.FluvialFlowRate(ref=1,
                                        flowrate=Q0,
                                        x_flux_direction=1.0,
                                        y_flux_direction=0.0)]

fluvial_heights = [fk.FluvialHeight(ref=2, height=2.)]

slides = [fk.Slide(ref=3), fk.Slide(ref=4)]

################################################################################
#
# Resolution:
#--------------------
#
#We loop over friction laws:
#

C = 0
for law, coef in FRICTION_PARAMS.items():

    print(" ")
    print(" ")
    print("                           SOLVING CASE {}                   ".format(C))
    print(" ")
    print(" ")

    simutime_l.append(fk.SimuTime(final_time=FINAL_TIME,
                                  time_iteration_max=100000,
                                  second_order=False))

    layer_l.append(fk.Layer(NL[law], triangular_mesh, topography=0.))

    primitives_l.append(fk.Primitive(triangular_mesh, layer_l[C],
                                     height=H0,
                                     QXinit=1.))

    PHYSICAL_PARAMS = {'friction_law':law,
                       'friction_coeff':coef,
                       'horizontal_viscosity':.02,
                       'vertical_viscosity':.02}

    problem_l.append(fk.Problem(simutime=simutime_l[C],
                                triangular_mesh=triangular_mesh,
                                layer=layer_l[C],
                                primitives=primitives_l[C],
                                numerical_parameters=NUMERICAL_PARAMS,
                                physical_parameters=PHYSICAL_PARAMS,
                                slides=slides,
                                fluvial_flowrates=fluvial_flowrates,
                                fluvial_heights=fluvial_heights))
    problem_l[C].solve()
    C += 1

################################################################################
#
# Plot velocity profile:
#-----------------------
#

if not args.nographics:
  cell = 233 #Middle domain

  fk_plt.set_rcParams()
  plt.rcParams["figure.figsize"] = [8, 6]
  fig = plt.figure()
  ax1 = fig.add_subplot(111)

  labels = []
  colors = ['blue', 'red', 'green', 'purple']
  markers = ['s', '*', 'o', 'v']

  N = NL['Navier']
  u = np.zeros((N))
  z = np.zeros((N))
  for L in range(N):
    z[L] = 0.5*(2.0/N) + L*(2.0/N)

  C = 0
  for law, coef in FRICTION_PARAMS.items():
      labels.append('{} (Coeff = {})'.format(law, coef))
      if law == 'Navier':
        u = problem_l[C].primitives.U[cell, :]
        fig = ax1.plot(u, z, color=colors[C], marker=markers[C], label=labels[C])
      else:
        u = problem_l[C].primitives.U[cell, :]*np.ones(N)
        fig = ax1.plot(u, z, color=colors[C], marker=markers[C], label=labels[C])
      ax1.set_title("Velocity profile in x = {}"
                  .format(triangular_mesh.triangulation.x[cell]))
      C += 1

  plt.legend(loc=2)
  plt.xlabel('U (m/s)')
  plt.ylabel('z (m)')
  plt.show()

################################################################################
#
#.. note::
#   As expected, Navier and Chézy as well as Strickler and Manning are equivalent
#   and lead to the same velocity profile.
#
