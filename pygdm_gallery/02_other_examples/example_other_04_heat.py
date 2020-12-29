# encoding: utf-8
"""
Example script, demonstrating heat generation in a planar plasmonic object

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




#==============================================================================
# setup simulation
#==============================================================================

## --- Setup structure (prism h=12nm, side=120nm in water on glass substrate)
mesh = 'hex'
step = 6.
## note: for the example in the doc. paper, step = 3.0 was used.
## for sake of simulation time we will use a far coarser discretization, which
## nevertheless will give a very good approximation
geometry = structures.prism(step, NSIDE=int(120/step), H=12/step, mesh=mesh)
geometry = structures.center_struct(geometry)

material = materials.gold()
n1, n2 = 1.45, 1.33          # water on glass

struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh),
                           with_radiation_correction=1)



## ---------- Setup incident field
field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = 0.0, kSign=-1)
wavelengths = np.linspace(500, 1000, 51)
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- Simulation initialization
sim = core.simulation(struct, efield)

visu.structure(sim, scale=0.5, borders=10)
print("N dipoles:", len(sim.struct.geometry))



#%%
#==============================================================================
# run the simulation
#==============================================================================
E = core.scatter(sim)
#E = core.scatter(sim, method='cupy', matrix_setup='numba', verbose=True)



#%%
## spectrum
field_kwargs = tools.get_possible_field_params_spectra(sim)[0]
wl, heat_spectrum = tools.calculate_spectrum(sim, field_kwargs, linear.heat)


## heat distribution in struct at plasmon resonance (around 880nm for the coarse mesh)
idx_struct = tools.get_closest_field_index(sim, dict(wavelength=880))
print("structure-plot wavelength: {}".format(wl[idx_struct]))
q = linear.heat(sim, idx_struct, return_value='structure')
## divide by cell volume --> nW/nm^3
q.T[3] /= (sim.struct.step**3/sim.struct.normalization)

#%%
#==============================================================================
# plot
#==============================================================================
plt.figure( figsize=(8,4) )
plt.subplot2grid( (1,4), (0,0), colspan=3)

## --- spectrum
plt.plot(wl, heat_spectrum/1.0E3, color='r')
plt.xlabel("wavelength (nm)")
plt.ylabel("Q (microwatt)", color='r')


## --- heat distribution inside prism
plt.subplot(144, aspect='equal')
plt.title("lambda={}nm".format(wl[idx_struct]))
im = visu.scalarfield(q, cmap='hot', show=0, zorder=1)
plt.colorbar(im, label='heat (nW/nm^3)', orientation='horizontal', ticks=[0,0.5,1,1.5,2])
# im.set_clim([0, 2])

visu.structure_contour(sim, lw=2, color='k', dashes=[2,2],
                       input_mesh='hex1', zorder=0, borders=10, show=0)



plt.show()

