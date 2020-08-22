"""
================================================================================
Ocean water state law
================================================================================

In this tutorial ocean international equation of state (IES 1980) used in 
Freshkiss3D to compute density based on temperature and salinity tracers is plotted.

"""

import numpy as np
import matplotlib.pyplot as plt
import freshkiss3d.extra.plots as fk_plt
from freshkiss3d.core.state_laws import *

PLOT_DERIVATIVE = False

fk_plt.set_rcParams()
plt.rcParams["figure.figsize"]=[12,5]

fig = plt.figure()
ax1 = fig.add_subplot(121)

P0 = 1.0
T = [0, 5, 10, 15, 20]
S = [0, 5, 10, 15, 20, 25, 30, 35]
Rho = np.zeros( (len(S)) )

#IES 1980: 
for I in range(len(T)):
    for J in range(len(S)):
        Rho[J] = Rho_IES1980(P0, T[I], S[J])

    ax1.plot(S, Rho, label='T = {} °C'.format(T[I]))

#Linear law: \rho = \rho_0 - \alpha*S
for J in range(len(S)):
    Rho[J] = Rho_salinity(S[J])
ax1.plot(S, Rho, color='k', ls=':', label='T = 10 °C (linear)')

ax1.legend(loc=4, shadow=True, title="Temperature")
ax1.set_xlabel('$S$ $(PSU)$')
ax1.set_ylabel('$\\rho$ $(kg/m^3)$')
ax1.set_xlim(0,35)
ax1.set_ylim(995,1030)

ax2 = fig.add_subplot(122)
if PLOT_DERIVATIVE: ax2b = ax2.twinx()

T = [-10, -5, 0, 5, 10, 15, 20, 25, 30]
S = [0, 5, 10, 15, 20, 25, 30, 35]
Rhob = np.zeros( (len(T)) )
dRho_estimate = np.zeros( (len(T)) )
P = 1
eps = 0.0001

#IES 1980:
for I in range(len(S)):
    for J in range(len(T)):
        Rhob[J] = Rho_IES1980(P0, T[J], S[I])
        dRho_estimate[J] = (Rho_IES1980(P0, T[J]+eps, S[I])-Rho_IES1980(P0, T[J], S[I]))/eps

    ax2.plot(T, Rhob, label='S = {} PSU'.format(S[I]))

    if PLOT_DERIVATIVE:
        ax2b.plot(T, dRho_estimate, label='dRho_dT,S = {} PSU'.format(S[I]))

#Quadratic law: \rho = \rho_0*(1 - \alpha*(T-4.0)**2)
for J in range(len(T)):
    Rhob[J] = Rho_temperature(T[J])
ax2.plot(T, Rhob, color='k', ls=':', label='S = 0 PSU (quadratic)')

ax2.legend(loc=3, shadow=True, title="Salinity")
ax2.set_xlabel('$T$ $(°C)$')
ax2.set_ylabel('$\\rho$ $(kg/m^3)$')
ax2.set_xlim(-5,25)
ax2.set_ylim(980,1030)
if PLOT_DERIVATIVE:
    ax2b.legend(loc=4, shadow=True, title="Salinity")
    ax2b.set_ylim(-0.2,0.2)

plt.show()

################################################################################
#
#.. note::
#
#   * If only temperature is prescribed in Freshkiss3D, IES is used with a default salinity of 0 g/L. You can set the default value with ``the ies1980_default_S0`` key of the ``physical_parameters`` dictionary.
#   * If only salinity is prescribed in Freshkiss3D, IES is used with a default temperature of 10 °C. You can set the default value with ``the ies1980_default_T0`` key of the ``physical_parameters`` dictionary.
#   

