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
from pyGDM2 import visu
from pyGDM2 import tools

import numpy as np
import matplotlib.pyplot as plt




# =============================================================================
# Simulation setup
# =============================================================================
## --- Setup structure
mesh = 'cube'
step = 7.0   # discretization in nm
L = 21       # cube side-length in nm
geometry = structures.rect_wire(step, L=L/step,H=L/step, W=L/step, mesh=mesh)
geometry.T[2] += step/2.

material = materials.dummy(2.0); MATERIAL = '20'
n1, n2 = 1.0, 1.0  # constant environment

struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))
struct = structures.center_struct(struct)



## --- Setup incident field (including dipole positions to evaluate)
x0 = np.linspace(-250, 250, 25)                  # x-scan pos.
y0 = np.linspace(-250, 250, 25)                  # y-scan pos.
z0 = struct.geometry.T[2].max() + step/2. + 15   # fixed height: 15nm above struct

kwargs = dict(x0=x0, y0=y0, z0=z0,    # positions where to evaluate
              mx=0,my=0,mz=0)         # dipole orientation (0,0,0) --> placeholder
wavelengths = [500]

## -- field-instances for electric and magnetic dipoles
efield_p = fields.efield(fields.dipole_electric, wavelengths, kwargs)
efield_m = fields.efield(fields.dipole_magnetic, wavelengths, kwargs)

## ---------- Simulation initialization
sim_p = core.simulation(struct, efield_p)
sim_m = core.simulation(struct, efield_m)


#%%
# =============================================================================
# Run simulation
# =============================================================================
print("\nEvaluation electric dipole decay rate..." )
SBB_p = core.decay_rate(sim_p, method='lu', verbose=True)

print("\nEvaluation magnetic dipole decay rate..." )
SBB_m = core.decay_rate(sim_m, method='lu', verbose=True)


#%%
# =============================================================================
# Plot decay for several orientations of the e-/m-dipole
# =============================================================================

## list of dipole test orientations
dp_list = [[1, 0, 0], 
           [0, 1, 0], 
           [0, 0, 1]]


plt.figure(figsize=(8,8))
for i, (mx,my,mz) in enumerate(dp_list):

    SBB_map_e = linear.decay_eval(sim_p, SBB_p[0], mx,my,mz, verbose=1)
    SBB_map_m = linear.decay_eval(sim_m, SBB_m[0], mx,my,mz, verbose=1)
    
    
    plt.subplot(3,2,2*i+1, aspect='equal')
    plt.title("{} dipole || ({},{},{})".format('electric',mx,my,mz))
    visu.scalarfield(SBB_map_e, cmap='jet', show=False)
    plt.colorbar(label='gamma / gamma_0')
    
    plt.subplot(3,2,2*i+2, aspect='equal')
    plt.title("{} dipole || ({},{},{})".format('magnetic',mx,my,mz))
    visu.scalarfield(SBB_map_m, cmap='jet', show=False)
    plt.colorbar(label='gamma / gamma_0')
    

plt.tight_layout()
plt.show()








