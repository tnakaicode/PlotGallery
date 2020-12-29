# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    Load the result of the "own problem" optimization, calculate the 
    scattering spectrum and plot to verify that a resonant structure was found.

"""


import numpy as np
import matplotlib.pyplot as plt
import copy


from pyGDM2 import linear
from pyGDM2 import tools
from pyGDM2 import visu
from pyGDM2 import structures
from pyGDM2 import materials

from pyGDM2 import core
from pyGDM2 import fields

from pyGDM2.EO.tools import get_best_candidate, get_best_candidate_f_x





#==============================================================================
# Load best candidate from optimization
#==============================================================================
## --- optimization file locations
results_folder = 'eo_out'
results_suffix = 'test_max_NF_E'

sim = get_best_candidate(results_folder, results_suffix, iteration=-1, verbose=True)
f, x = get_best_candidate_f_x(results_folder, results_suffix, iteration=-1)
print f, x


#tools.save_simulation(sim, "max_nearfield_E_-100_150.sim")

#==============================================================================
# calculate nearfield map
#==============================================================================
## --- map
MAP = tools.generate_NF_map_XY(-550,550,51, -250,250,51, Z0=80)

Es, Etot, Bs, Btot = linear.nearfield(sim, field_index=0, MAP=MAP)

#%%
plt.figure(figsize=(7, 3.))
plt.subplot(121, aspect='equal')
plt.title("E-field")
im = visu.structure_contour(sim, color='w', s=1, show=0)
im = visu.vectorfield_color(Es, show=0, interpolation='bicubic')
plt.colorbar(label=r'$|\mathbf{E}|^2/|\mathbf{E}_0|^2$')
plt.xlabel("X (nm)")
plt.ylabel("Y (nm)")
plt.clim( [0, im.get_clim()[1]] )


plt.subplot(122, aspect='equal')
plt.title("B-field")
im = visu.structure_contour(sim, color='w', s=1, show=0)
im = visu.vectorfield_color(Bs, show=0, interpolation='bicubic')
plt.colorbar(label=r'$|\mathbf{B}|^2/|\mathbf{B}_0|^2$')
plt.xlabel("X (nm)")
plt.ylabel("Y (nm)")
plt.clim( [0, im.get_clim()[1]] )

plt.tight_layout()
plt.show()


