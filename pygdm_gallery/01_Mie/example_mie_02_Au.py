# encoding: utf-8
"""
Example script, comparing pyGDM with Mie theory for a gold sphere

"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import tools
from pyGDM2 import linear
from pyGDM2 import visu




## --- load pre-calculated Mie-data
wl_mie, qext_mie, qsca_mie = np.loadtxt("scat_mie_Au_D50nm.txt").T
qabs_mie = qext_mie - qsca_mie


#==============================================================================
# pyGDM setup
#==============================================================================
## --- Setup incident field
field_generator = fields.planewave
## log-interval spectrum (denser at low lambda):
wavelengths = np.exp(np.linspace(np.log(400), np.log(700), 30))
kwargs = dict(theta = [0.0])
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## --- Setup geometry (sphere D=50nm in vacuum)
scale_factor = 1.38     # this value was used in doc.-paper example
step = 6.25/scale_factor
radius = 4.*scale_factor
geometry = structures.sphere(step, R=radius, mesh='hex', ORIENTATION=2)

material = materials.gold()
n1, n2 = 1.0, 1.0     # vacuum env.

struct = structures.struct(step, geometry, material, n1,n2, 
                                   structures.get_normalization('hex'))


sim = core.simulation(struct, efield)

visu.structure(sim)
print('(hex) ----- N_dipoles =', len(sim.struct.geometry), end='')

#%%
#==============================================================================
# run the simulations
#==============================================================================
# E = core.scatter(sim, method='lu', verbose=True)
E = core.scatter(sim, method='cupy', matrix_setup='numba', verbose=True)

## extinction spectrum
field_kwargs = tools.get_possible_field_params_spectra(sim)[0]
wl, spec = tools.calculate_spectrum(sim, field_kwargs, linear.extinct)
a_ext, a_sca, a_abs = spec.T
a_geo = tools.get_geometric_cross_section(sim)



#%%
#==============================================================================
# plot
#==============================================================================
plt.figure(figsize=(5,4), dpi=100)
plt.title("gold sphere, D=50nm")

## --- Mie
plt.plot(wl_mie, qext_mie, 'b--', dashes=[2,1],label='ext.')
plt.plot(wl_mie, qabs_mie, 'g--', dashes=[2,1],label='abs.')
plt.plot(wl_mie, qsca_mie, 'r--', dashes=[2,1],label='scat.')

## --- pyGDM
plt.scatter(wl, a_ext/a_geo, marker='x', linewidth=1.5,s=25, color='b', label='')
plt.scatter(wl, a_abs/a_geo, marker='x', linewidth=1.5,s=25, color='g', label='')
plt.scatter(wl, a_sca/a_geo, marker='x', linewidth=1.5,s=25, color='r', label='')

plt.xlim(400,700)

## --- for legend only
plt.plot([0], [0], 'k--', dashes=[2,1], label='Mie')
plt.scatter([0], [0], marker='x', linewidth=1.5, color='k', label='pyGDM')
## -- legend
plt.legend(loc='best', fontsize=12)


plt.xlabel("wavelength (nm)")
plt.ylabel("ext. / scat. / abs. efficiency")
# plt.xlim( [wl.min(), wl.max()] )
plt.ylim( [0, 1.7] )



plt.tight_layout()
plt.show()
