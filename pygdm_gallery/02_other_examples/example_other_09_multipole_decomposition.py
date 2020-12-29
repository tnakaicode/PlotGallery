# encoding: utf-8
"""
Example script, demonstrating pyGDM multipole decomposition

"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields
from pyGDM2 import core
from pyGDM2 import visu
from pyGDM2 import tools
from pyGDM2 import linear


# =============================================================================
#
#                               !! warning !!
#
# multipole decomposition is not finally tested beta-functionality of pyGDM! 
# Use with caution and at own risk
# =============================================================================

## CUDA-based inversion on GPU
method = 'cupy'




## --- simulation initialization ---
mesh = 'cube'
step = 10
#geometry = structures.nanodisc(step, R=(175/step), H=int(280/step), mesh=mesh)
geometry = structures.rect_wire(step, L=int(np.round(160/step)), 
                                      W=int(np.round(160/step)), 
                                      H=int(np.round(160/step)), mesh=mesh)
material = materials.silicon()
norm = structures.get_normalization(mesh=mesh)
n1 = n2 = n3 = 1.0

struct = structures.struct(step, geometry, material, n1,n2, norm, n3=n3)

## incident field: lin. pol plane wave
field_generator = fields.planewave
wavelengths = np.linspace(530, 830, 31)
kwargs = dict(theta=0.0, kSign=-1)
efield = fields.efield(field_generator, 
               wavelengths=wavelengths, kwargs=kwargs)

## create simulation object
sim = core.simulation(struct, efield)


visu.structure(sim)
print("N dp={}".format(len(geometry)))

## --- run the main simulation ---
core.scatter(sim, matrix_setup='numba', method=method)


#%%
## -- spectra of extinction sections per multipole moment
wl, spec1 = tools.calculate_spectrum(sim, 0, linear.extinct)
ex, sc, ab = spec1.T
wl, spec2 = tools.calculate_spectrum(sim, 0, linear.mutlipole_decomp_extinct)
ex_p, ex_m, ex_q, ex_mq = spec2.T

#plt.figure(figsize=(10,7))
plt.plot(wl, ex, label='extinct')
plt.plot(wl, ex_p, label='p')
plt.plot(wl, ex_m, label='m')
plt.plot(wl, ex_q, label='q')
plt.plot(wl, ex_mq, label='mq')
plt.plot(wl, ex_p + ex_m + ex_q + ex_mq, label='multipole sum', dashes=[2,2])

plt.legend()
plt.title("multipole decomposition")
plt.xlabel("wavelength (nm)")
plt.ylabel("extinction cross section (nm^2)")
#plt.savefig("example_multipole_decomposition.png", dpi=150)
plt.show()

#%%
## -- spectra of multipole moments
wl, spec_dpdecomp = tools.calculate_spectrum(sim, 0, linear.mutlipole_decomp)
p = np.array([decomp[0] for decomp  in spec_dpdecomp])
m = np.array([decomp[1] for decomp  in spec_dpdecomp])
q = np.array([decomp[2] for decomp  in spec_dpdecomp])
mq = np.array([decomp[3] for decomp  in spec_dpdecomp])

plt.plot(wl, np.abs(p.T[0]), label='|p_x|')
plt.plot(wl, np.abs(m.T[1]), label='|m_y|')
plt.legend()
plt.xlabel("wavelength (nm)")
plt.ylabel("multipole moment (a.u.)")
plt.show()
