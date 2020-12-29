# encoding: utf-8
"""
Example script, demonstrating polarization conversion from an L-shape 
plasmonic dimer antenna

"""
from __future__ import print_function, division

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import tools
from pyGDM2 import linear
from pyGDM2 import visu

import numpy as np
import matplotlib.pyplot as plt




#==============================================================================
# config sim.
#==============================================================================
## --- Setup structure
mesh = 'cube'
step = 15.0
geometry = structures.lshape_rect_nonsym(step, 
                            L1=14,W1=3, L2=14,W2=3, H=4, DELTA=1, mesh=mesh)
material = materials.gold()

n1, n2 = 1.0, 1.0  # constant environment

struct = structures.struct(step, geometry, material, n1,n2, 
                                       structures.get_normalization(mesh))


## --- Setup incident field
field_generator = fields.planewave        # planwave excitation
wavelengths = np.linspace(600, 1500, 45)  # spectrum
kwargs = dict(theta = [0.0])
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## --- Simulation initialization
sim = core.simulation(struct, efield)

visu.structure(sim.struct.geometry, scale=1)
print("N dipoles:", len(sim.struct.geometry))



#%%
#==============================================================================
# Simulation
#==============================================================================
core.scatter(sim, method='lu', verbose=True)
#core.scatter(sim, method='cupy', matrix_setup='numba', verbose=True)


#%%
## --- total scat.
kwargs = dict(polarizerangle='none', return_value='int_Es', tetamax=np.pi/2.)
wl, spec_farfield = tools.calculate_spectrum(sim, 0, linear.farfield, **kwargs)

## --- scat polarized along X
kwargs = dict(polarizerangle=0, return_value='int_Es', tetamax=np.pi/2.)
wl, spec_farfield0 = tools.calculate_spectrum(sim, 0, linear.farfield, **kwargs)

## --- scat polarized along Y
kwargs = dict(polarizerangle=90, return_value='int_Es', tetamax=np.pi/2.)
wl, spec_farfield90 = tools.calculate_spectrum(sim, 0, linear.farfield, **kwargs)


#%%
#==============================================================================
# PLOT
#==============================================================================
plt.figure()

plt.plot(wl, spec_farfield, 'k--', lw=0.75, dashes=[2,2], label='tot. scat.')
plt.plot(wl, spec_farfield0, 'b', lw=0.75, label=r'in $X$, out $X$')
plt.plot(wl, spec_farfield90, 'r', lw=0.75, label=r'in $X$, out $Y$')

plt.legend(loc='best', frameon=0)
plt.xlabel("wavelength (nm)")
plt.ylabel(r"$\sigma_{\mathsf{scat.}}$ (nm$^2$)")
plt.xlim([600,1500])


## --- inset for structure geometry
plt.axes([0.63,0.34, 0.31,0.31], aspect='equal')
plt.axis('off')

visu.structure(sim, show=False, color="#c7a800")
visu.structure_contour(sim, lw=0.5, color='.5', show=False, borders=10)

plt.text(105, 50, r"$\mathbf{E}_{\mathsf{in}}$", ha='center', va='bottom', color='b')
plt.arrow( 80, 40, 50, 0, width=2, head_width=15, head_length=20, color='b', clip_on=False)




plt.show()



