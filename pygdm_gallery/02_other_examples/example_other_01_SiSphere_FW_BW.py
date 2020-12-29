# encoding: utf-8
"""
Example script, FW/BW resolved scattering from silicon sphere

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
# pyGDM setup
#==============================================================================

## --- Setup incident field
field_generator = fields.planewave
## log-interval spectrum (denser at low lambda):
wavelengths = np.exp(np.linspace(np.log(300), np.log(1000), 30))
kwargs = dict(theta = [0.0])
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## --- Setup geometry (sphere D=150nm in vacuum)
## note: scale_factor = 2.7 was used for the documentation example
scale_factor = 1.4
step = 18.75/scale_factor
radius = 4.*scale_factor
geometry = structures.sphere(step, R=radius, mesh='hex', ORIENTATION=2)

material = materials.silicon()
n1, n2 = 1.0, 1.0     # vacuum env.

struct = structures.struct(step, geometry, material, n1,n2, 
                                   structures.get_normalization('hex'))


sim = core.simulation(struct, efield)

visu.structure(sim)
print('(hex) ----- N_dipoles =', len(sim.struct.geometry), end='')

#%%
#==============================================================================
# run the simulation
#==============================================================================
E = core.scatter(sim, method='lu', verbose=True)
#E = core.scatter(sim, method='cupy', matrix_setup='numba', verbose=True)

## FW and BW scattering spectrum
field_kwargs = tools.get_possible_field_params_spectra(sim)[0]
wl, scat_fw = tools.calculate_spectrum(sim, field_kwargs, linear.farfield, 
                                      tetamin=np.pi/2., tetamax=np.pi, 
                                      return_value='int_Es')
wl, scat_bw = tools.calculate_spectrum(sim, field_kwargs, linear.farfield, 
                                      tetamin=0, tetamax=np.pi/2., 
                                      return_value='int_Es')


#%%
#==============================================================================
# plot
#==============================================================================
plt.figure()
plt.title(r"D=150nm Si sphere")


## --- scattering spectra FW & BW
plt.plot(wl, scat_fw, 'r', label='FW.')
plt.plot(wl, scat_bw, 'b', label='BW.')

plt.xlabel("wavelength (nm)")
plt.ylabel(r"scat. cross-section (nm^2)")
plt.xlim(400,800)

plt.plot([0], [0], color='g', dashes=[2,1], label='FW/BW')  # for legend entry
plt.legend(loc='center', frameon=False, ncol=1, bbox_to_anchor=(0.83, 0.3))



## --- logscale FW/BW ratio on right y-axis
plt.twinx()
plt.plot(wl, scat_fw/scat_bw, color='g', dashes=[2,1])
plt.plot([400,800], [1,1], color='k', lw=0.5, dashes=[2,1], label='FW/BW=1')

plt.ylabel(r"FW/BW ratio", rotation=270, labelpad=8, color='g')
plt.yscale('log')
plt.xlim( [400, 800] )
plt.ylim( [0.1, 10] )
plt.legend(loc='center', frameon=False, ncol=1, bbox_to_anchor=(0.8, 0.55))



plt.tight_layout()
plt.show()


