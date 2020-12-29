# encoding: utf-8
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt


from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import nonlinear
from pyGDM2 import visu
from pyGDM2 import tools





## ---------- Setup structure
mesh = 'cube'
## -- note: in the paper example, a stepsize of 20nm was used. 
##          We increase the step for the sake of a shorter simulation runtime.
step = 30.0
geometry = structures.rect_split_ring(step, L1=800/step-1, L2=400/step-1, 
                                         W=180/step-1, H=int(60/step), mesh=mesh)

material = materials.dummy(2.0)

n1, n2 = 1.0, 1.0  # constant environment

struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))
struct = structures.center_struct(struct)



## --- raster-scan height: at top-surface of structure
Z_scan = geometry.T[2].max()

#remap = adapt_map_to_structure_mesh(sim)
MAP = tools.generate_NF_map(-550,550,25, -310,310,15, Z_scan)
remap = MAP


## ---------- Setup incident field
kwargs_focused = []
kwargs_dipole = []
for x,y,z in remap.T:
    ## keys for focused illumination (TPL-method)
    kwargs_focused.append( dict(theta=0, spotsize=100, kSign=-1, xSpot=x, ySpot=y) )
    kwargs_focused.append( dict(theta=90, spotsize=100, kSign=-1, xSpot=x, ySpot=y) )
    
    ## keys for dipole emitter scan ("real" LDOS)
    kwargs_dipole.append( dict(x0=x, y0=y, z0=z, mx=0,my=0,mz=0) )


wavelengths = [600]
efield_focused = fields.efield(fields.focused_planewave, wavelengths=wavelengths, kwargs=kwargs_focused)
efield_dipole = fields.efield(fields.dipole_electric, wavelengths=wavelengths, kwargs=kwargs_dipole)


## ---------- Simulation initialization
sim_foc = core.simulation(struct, efield_focused)
sim_dp = core.simulation(struct, efield_dipole)



#%%
### --------- Main Simulations
## scattering (TPL method)
#core.scatter(sim_foc, verbose=True)
core.scatter(sim_foc, matrix_setup='numba', method='cupy', verbose=True)

## decay rate (LDOS)
#core.decay_rate(sim_dp, verbose=True)
core.decay_rate(sim_dp, matrix_setup='numba', method='cupy', verbose=True)

#%%

## --- calculate TPL rasterscan maps
TPL0 = tools.calculate_rasterscan(sim_foc, 0, nonlinear.tpl_ldos, nonlin_order=1)
TPL90 = tools.calculate_rasterscan(sim_foc, 1, nonlinear.tpl_ldos, nonlin_order=1)

## --- calculate decay-rate rasterscan maps
gamma_scan_X = linear.decay_eval(sim_dp, 0, 1, 0, 0)
gamma_scan_Y = linear.decay_eval(sim_dp, 0, 0, 1, 0)



plt.figure(figsize=(10,6))

## --- plot "TPL-LDOS"
plt.subplot(231, aspect='equal'); plt.title("TPL-LDOS along X")
visu.scalarfield(TPL0, cmap='jet', show=False)
visu.structure_contour(sim_dp, color='w', input_mesh=mesh, show=False)


plt.subplot(232, aspect='equal'); plt.title("TPL-LDOS along Y")
visu.scalarfield(TPL90, cmap='jet', show=False)
visu.structure_contour(sim_dp, color='w', input_mesh=mesh, show=False)


TPL_tot = [TPL0[0], (TPL0[1]+TPL90[1])/2.]

plt.subplot(233)
plt.title("tot. LDOS via 'TPL'-method\nfocal spot size = {}nm".format(int(sim_foc.efield.kwargs[0]['spotsize'])))
visu.scalarfield(TPL_tot, cmap='jet', show=False)
visu.structure_contour(sim_dp, color='w', input_mesh=mesh, show=False)



## --- plot LDOS via field-susceptibility ("decay-rate method")
plt.subplot(234)
plt.title("LDOS via Im(S) X")
visu.scalarfield(gamma_scan_X, cmap='jet', show=False)
visu.structure_contour(sim_dp, color='w', input_mesh=mesh, show=False)


plt.subplot(235)
plt.title("LDOS via Im(S) Y")
visu.scalarfield(gamma_scan_Y, cmap='jet', show=False)
visu.structure_contour(sim_dp, color='w', input_mesh=mesh, show=False)


gamma_scan_tot = gamma_scan_X
gamma_scan_tot.T[3] += gamma_scan_Y.T[3]
gamma_scan_tot.T[3] /= 2.0

plt.subplot(236)
plt.title("LDOS via Im(S), tot x/y")
visu.scalarfield(gamma_scan_tot, cmap='jet', show=False)
visu.structure_contour(sim_dp, color='w', input_mesh=mesh, show=False)



plt.tight_layout()
plt.show()
