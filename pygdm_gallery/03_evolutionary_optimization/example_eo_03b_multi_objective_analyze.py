# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    evolutionary optimizaton of plasmonic nanostructure geometry for 
    directional scattering

"""
from __future__ import print_function, division

import copy
import numpy as np
import matplotlib.pyplot as plt

import pyGDM2.EO.tools as EOtools
from pyGDM2 import core
from pyGDM2 import fields
from pyGDM2 import tools
from pyGDM2 import visu
from pyGDM2 import linear



## --- The EO-tools need the problem/model definitions in namespace
from example_eo_03_multi_objective import ownMultiObjectiveProblem


filename = "emo_test.eo"
idx_pareto = 0
idx_individual = 15

all_paretos, all_sims, all_x = EOtools.get_pareto_fronts(filename, iteration=-1)
pareto      = all_paretos[idx_pareto]
pareto_sims = all_sims[idx_pareto]


#EOtools.plot_pareto_2d(pareto)

EOtools.plot_all_pareto_fronts_2d(all_paretos)


sim = pareto_sims[idx_individual]





# =============================================================================
# Print all structures on pareto-front
# =============================================================================
reduced_sims = []
reduced_geos = []

for i, s in enumerate(pareto_sims):
    tdproj = tools.get_geometry_2d_projection(s)
    tdproj = list( np.array([[x,y] for (x,y,z) in tdproj]).flatten() )
    if tdproj not in reduced_geos:
        reduced_geos.append(tdproj)
        reduced_sims.append([i, s])
    

plt.figure(figsize=(10,10))
N = len(reduced_sims)
for i,[i_pareto, s] in enumerate(reduced_sims):
    N_plots = int(np.ceil(np.sqrt(N)))
    plt.subplot(N_plots,N_plots,i+1, aspect='equal')
    plt.title("front-idx={}".format(i_pareto))
    visu.structure(s, show=False)

plt.show()


#%%
#==============================================================================
# setup new simulation to calculate spectrum
#==============================================================================
## --- structure
struct = copy.deepcopy(sim.struct)

## --- incident field
field_generator = fields.planewave        # planwave excitation
wavelengths = np.arange(400, 1615, 30)  # spectrum
kwargs = dict(theta = [0.0, 90.0])          # 0/90 deg polarizations
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)



## --- simulation
sim_spectrum = core.simulation(struct, efield)


#==============================================================================
# run simulation for the spectrum
#==============================================================================
core.scatter(sim_spectrum, verbose=0)
#%%

## spectrum
field_kwargs = tools.get_possible_field_params_spectra(sim_spectrum)[0]
wl, spec_ext0 = tools.calculate_spectrum(sim_spectrum, field_kwargs, linear.extinct)
asca0 = spec_ext0.T[1]

field_kwargs = tools.get_possible_field_params_spectra(sim_spectrum)[1]
wl, spec_ext90 = tools.calculate_spectrum(sim_spectrum, field_kwargs, linear.extinct)
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





#%%
#tools.save_simulation(sim_spectrum, "simulation_mo_gold_cross_f1_{:.2f}_f2_{:.2f}_spec.pcl".format( 
#                            pareto[testidx][0], pareto[testidx][1] ))

print(np.round(pareto[idx_individual],2))
