
# coding: utf-8

# Heat generation
# ==================
# 
# In this example, light induced heat generation inside a planar plasmonic nano-structure will be demonstrated, reproducing results of Baffou *et al.* [1].
# 
# [1] Baffou, G. *Heat generation in plasmonic nanostructures: Influence of morphology*. **Applied Physics Letters** 94, 153109 (2009) (https://doi.org/10.1063/1.3116645)
# 
# Setup the simulation
# ------------------------

# In[1]:


## --- load the modules
from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import visu
from pyGDM2 import tools

import numpy as np
import matplotlib.pyplot as plt


## --- Setup structure (prism h=12nm, side=120nm in water on glass substrate)
step = 6.0
geometry = structures.prism(step, NSIDE=int(120/step), H=18/step, mesh='hex')
geometry = structures.center_struct(geometry)

material = materials.gold()
n1, n2 = 1.45, 1.33          # water on glass

struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization('hex'))


## --- Setup incident field
field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = 0.0, kSign=-1)
wavelengths = np.linspace(500, 1000, 51)
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## --- Simulation initialization
sim = core.simulation(struct, efield)


# Heat spectrum and -distribution inside structure
# ---------------------------------------------
# 
# After the main simulation routine (*core.scatter*), we calculate the spectrum of the total deposited heat as well as the heat-distribution inside the nano-structure at the plasmon resonance ($\lambda_{p} \approx 820\,$nm).

# In[2]:


## --- main simulation
E = core.scatter(sim, verbose=1)


## --- heat spectrum
wl, heat_spectrum = tools.calculate_spectrum(sim, 0, linear.heat)

## --- heat distribution in struct at plasmon resonance
idx_struct = tools.get_closest_field_index(sim, dict(wavelength=820))
q = linear.heat(sim, idx_struct, return_value='structure')

## --- divide heat-distribution by cell volume --> nW/nm^3
q.T[3] /= (sim.struct.step**3/sim.struct.normalization)


# Plot
# ----------
# 
# Let's plot the spectrum and the heat distribution inside the structure:

# In[3]:


plt.figure( figsize=(8,4) )
plt.subplot2grid( (1,4), (0,0), colspan=3)

## --- spectrum
plt.plot(wl, heat_spectrum/1.0E3, color='r')
plt.xlabel("wavelength (nm)")
plt.ylabel("Q (microwatt)", color='r')


## --- heat distribution inside prism
plt.subplot(144, aspect='equal')
plt.title("lambda={}nm".format(wl[idx_struct]))
im = visu.scalarfield(q, cmap='hot', show=0, zorder=0, slice_level=-9999, interpolation=None)
plt.colorbar(label='heat (nW/nm^3)', orientation='horizontal', 
                                         ticks=[0,0.5,1,1.5,2])
plt.clim([0, 2])

visu.structure_contour(sim, lw=2, color='k', dashes=[2,2],
                       input_mesh='hex', zorder=3, borders=10, show=0)


plt.savefig("heat_generation.png", dpi=150)
plt.show()


# This is in pretty good agreement with [1] (see above for reference).
