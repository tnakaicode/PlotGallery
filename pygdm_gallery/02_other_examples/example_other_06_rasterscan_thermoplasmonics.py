# encoding: utf-8
"""
Example script, demonstrating raster-scan simulations

"""
from __future__ import print_function, division

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import nonlinear
from pyGDM2 import visu
from pyGDM2 import tools

import numpy as np
import matplotlib.pyplot as plt



#==============================================================================
# simulation setup
#==============================================================================
## --- Setup structure
step = 20.0
geometry = structures.rhombus(step, L=int(520/step), H=1, alpha=60, mesh='hex')
geometry = structures.center_struct(geometry)

material = materials.gold()
n1, n2 = 1.33, 1.33  # constant environment (water)

struct = structures.struct(step, geometry, material, n1,n2, 
                                   structures.get_normalization('hex'))

## --- Setup incident field
field_generator = fields.focused_planewave        # planwave excitation

## 50nm spotsize: LDOS; 200nm spotsize: TPL map
kwargs = dict(theta = [0, 90], spotsize=[200], kSign=-1, 
              xSpot=np.linspace(-500, 500, 33), 
              ySpot=np.linspace(-500, 500, 33))
wavelengths = [750]
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- Simulation initialization
sim = core.simulation(struct, efield)


visu.structure(sim.struct.geometry, scale=0.5)
print("N dipoles:", len(sim.struct.geometry))

rasterscan_fieldconfigs = tools.get_possible_field_params_rasterscan(sim)
print('\n\navailable rasterscan configurations' )
for i, p in enumerate(rasterscan_fieldconfigs):
    print("index {}: {}".format(i, p))

#%%
#==============================================================================
# run the simulation
#==============================================================================
_E = core.scatter(sim, method='lu')
#_E = core.scatter(sim, matrix_setup='numba', method='cupy')


#%%
#==============================================================================
# calculate the raster-scans
#==============================================================================
## raster-scan indices 0,1: 0,90 deg

## --- TPL
print("calculating TPL...")
TPL0 = tools.calculate_rasterscan(sim, 0, nonlinear.tpl_ldos)
TPL90 = tools.calculate_rasterscan(sim, 1, nonlinear.tpl_ldos)


## --- heat
print("calculating heat...")
Q0 = tools.calculate_rasterscan(sim, 0, linear.heat, return_units='uW')
Q90 = tools.calculate_rasterscan(sim, 1, linear.heat, return_units='uW')


## --- temperature increase
print("calculating temperature rise at (0,0,150)...")
r_probe = (0, 0, 150)
DT0 = tools.calculate_rasterscan(sim, 0, linear.temperature, r_probe=r_probe, kappa_env=0.6)
DT90 = tools.calculate_rasterscan(sim, 1, linear.temperature, r_probe=r_probe, kappa_env=0.6)



#%%
#==============================================================================
# plot
#==============================================================================
plt.figure(figsize=(10,6))

from matplotlib.ticker import MaxNLocator
MaxNLocator.default_params['nbins'] = 3


## --- TPL
plt.subplot(2,3,1, aspect='equal')
plt.xticks([]); plt.yticks([]); plt.title("TPL, pol. 0")
im = visu.scalarfield(TPL0, cmap='jet', show=False)
plt.colorbar(im, orientation='horizontal', shrink=0.8, aspect=12)
visu.structure_contour(geometry, color='w', dashes=[2,2], lw=1.0, input_mesh='hex_onelayer', show=0)

plt.subplot(2,3,4, aspect='equal')
plt.xticks([]); plt.yticks([]); plt.title("TPL, pol. 90")
im = visu.scalarfield(TPL90, cmap='jet', show=False)
plt.colorbar(im, orientation='horizontal', shrink=0.8, aspect=12)
visu.structure_contour(geometry, color='w', dashes=[2,2], lw=1.0, input_mesh='hex_onelayer', show=0)


## --- heat
plt.subplot(2,3,2, aspect='equal')
plt.xticks([]); plt.yticks([]); plt.title("Q, pol. 0")
im = visu.scalarfield(Q0, cmap='inferno', show=False)
plt.colorbar(im, orientation='horizontal', shrink=0.8, aspect=12)
visu.structure_contour(geometry, color='w', dashes=[2,2], lw=1.0, input_mesh='hex_onelayer', show=0)

plt.subplot(2,3,5, aspect='equal')
plt.xticks([]); plt.yticks([]); plt.title("Q, pol. 90")
im = visu.scalarfield(Q90, cmap='inferno', show=False)
plt.colorbar(im, orientation='horizontal', shrink=0.8, aspect=12)
visu.structure_contour(geometry, color='w', dashes=[2,2], lw=1.0, input_mesh='hex_onelayer', show=0)


## --- temperature rise
plt.subplot(2,3,3, aspect='equal')
plt.xticks([]); plt.yticks([]); plt.title("DT, pol. 0")
im = visu.scalarfield(DT0, cmap='hot', show=False)
plt.colorbar(im, orientation='horizontal', shrink=0.8, aspect=12)
visu.structure_contour(geometry, color='w', dashes=[2,2], lw=1.0, input_mesh='hex_onelayer', show=0)

plt.subplot(2,3,6, aspect='equal')
plt.xticks([]); plt.yticks([]); plt.title("DT, pol. 90")
im = visu.scalarfield(DT90, cmap='hot', show=False)
plt.colorbar(im, orientation='horizontal', shrink=0.8, aspect=12)
visu.structure_contour(geometry, color='w', dashes=[2,2], lw=1.0, input_mesh='hex_onelayer', show=0)



plt.show()