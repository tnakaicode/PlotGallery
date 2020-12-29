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

from pyGDM2.EO.tools import get_best_candidate





#==============================================================================
# Load best candidate from optimization
#==============================================================================
## --- optimization results file
results_filename = 'eo_Qscat.eo'

sim = get_best_candidate(results_filename, iteration=-1, verbose=True)


#==============================================================================
# setup new simulation to calculate spectrum
#==============================================================================
## --- structure
struct = copy.deepcopy(sim.struct)


## --- incident field
field_generator = fields.planewave        # planwave excitation
wavelengths = np.arange(600, 1410, 20)    # spectrum
kwargs = dict(theta = [0.0, 90.0])        # 0/90 deg polarizations
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## --- simulation
sim_spectrum = core.simulation(struct, efield)


#==============================================================================
# run simulation for the spectrum
#==============================================================================
core.scatter(sim_spectrum, method='lu')


## spectrum
wl, spec_ext0 = tools.calculate_spectrum(sim_spectrum, 0, linear.extinct)
asca0 = spec_ext0.T[1]

wl, spec_ext90 = tools.calculate_spectrum(sim_spectrum, 1, linear.extinct)
asca90 = spec_ext90.T[1]

geom_cs = tools.get_geometric_cross_section(sim_spectrum)


#%%
## --- plot
plt.figure(figsize=(10,5))

## --- spectra
plt.subplot2grid((1,5), (0,0), colspan=3)
plt.title("scattering spectrum")
plt.plot(wl, asca0/geom_cs, label="0deg")
plt.plot(wl, asca90/geom_cs, label="90deg")

plt.legend(loc='best', fontsize=10)
plt.xlabel("wavelength (nm)")
plt.ylabel("Q_scat")


## --- structure
plt.subplot2grid((1,5), (0,3), colspan=2, aspect="equal")
plt.title('structure geometry')
visu.structure(sim_spectrum, show=False)
    
plt.show()



