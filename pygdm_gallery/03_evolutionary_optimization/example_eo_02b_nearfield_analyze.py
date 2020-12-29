# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    Load the result of the "own problem" optimization, calculate the 
    scattering spectrum and plot to verify that a resonant structure was found.

"""
from __future__ import print_function, division

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

from pyGDM2.EO.tools import get_best_candidate, get_best_candidate_f_x, get_problem





#==============================================================================
# Load best candidate from optimization
#==============================================================================
## --- optimization results file
results_filename = 'eo_NF.eo'

sim = get_best_candidate(results_filename, iteration=-1, verbose=True)
problem = get_problem(results_filename)
f, x, N_improvements = get_best_candidate_f_x(results_filename, iteration=-1)


print('\n ==================================================')
print("Problem:", problem.get_extra_info())
print(" target position: {}".format(problem.r_probe.T[0]))
print(" optimization: Nr of improvements {}".format(N_improvements))
print(" optimization: best fitness {}".format(f))
print('===================================================\n')


#==============================================================================
# calculate nearfield map
#==============================================================================
## --- map 80nm above substrate
MAP = tools.generate_NF_map_XY(-300,300,51, -300,300,51, Z0=80)

Es, Etot, Bs, Btot = linear.nearfield(sim, field_index=0, r_probe=MAP)


#%%
plt.figure()
plt.subplot(aspect='equal')
plt.title("E-field")

im = visu.structure_contour(sim, color='w', dashes=[2,2], show=0, zorder=10)
im = visu.vectorfield_color(Es, show=0, interpolation='bicubic')
plt.colorbar(label=r'$|\mathbf{E}|^2/|\mathbf{E}_0|^2$')

plt.scatter(problem.r_probe[0], problem.r_probe[1], marker='x', lw=3, s=75, color='k', label='target')
plt.legend(loc='best', fontsize=8)

plt.xlabel("X (nm)")
plt.ylabel("Y (nm)")
plt.clim( [0, im.get_clim()[1]] )


plt.tight_layout()
plt.show()


