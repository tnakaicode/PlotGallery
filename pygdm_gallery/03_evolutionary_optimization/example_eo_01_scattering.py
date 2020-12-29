# encoding: utf-8
"""
Created on June 1, 2017

@author: P. R. Wiecha

"""
from __future__ import print_function, division

from pyGDM2 import core
from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields
from pyGDM2 import linear
from pyGDM2 import tools
from pyGDM2 import visu

from pyGDM2.EO.core import run_eo
from pyGDM2.EO.problems import ProblemScat
from pyGDM2.EO.models import RectangularAntenna
from pyGDM2.EO.tools import get_best_candidate

import matplotlib.pyplot as plt
import numpy as np
import copy



#==============================================================================
# Setup pyGDM part
#==============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 15
material = materials.gold()   # structure material
n1, n2 = 1.0, 1.0             # vacuum environment

## --- Empty dummy-geometry, will be replaced on run-time by EO trial geometries
geometry = []       
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))


## ---------- Setup incident field
field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = [0.0])              # target lin. polarization angle
wavelengths = [1000]                      # target wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- Simulation initialization
sim = core.simulation(struct, efield)


#==============================================================================
# setup evolutionary optimization
#==============================================================================
## --- structure model: Rectangular planar antenna of fixed height
limits_W   = [2, 20]  # units of "step"
limits_L   = [2, 20]  # units of "step"
limits_pos = []   # units of nm, [] -->  no shift allowed
height = 3    # units of "step"
model = RectangularAntenna(sim, limits_W, limits_L, limits_pos, height)

## --- optimization problem: Scattering
opt_target = 'Qscat'  # 'Qscat' --> scat. efficiency
problem = ProblemScat(model, opt_target=opt_target)


## --- filename to save results 
results_filename = 'eo_Qscat.eo'

## --- size of population
population = 15          # Nr of individuals

## --- stop criteria
max_time = 60            # seconds
max_iter = 20            # max. iterations
max_nonsuccess = 5      # max. consecutive iterations without improvement

## --- other config
generations = 1          # generations to evolve between status reports
plot_interval = 5        # plot each N improvements
save_all_generations = False

##  Use algorithm "sade" (jDE variant, a self-adaptive form of differential evolution)
import pygmo as pg
algorithm = pg.sade
algorithm_kwargs = dict()   # optional kwargs passed to the algorithm


eo_dict = run_eo(problem,
                 population=population,
                 algorithm=algorithm,
                 plot_interval=plot_interval, 
                 generations=generations, 
                 max_time=max_time, max_iter=max_iter, max_nonsuccess=max_nonsuccess,
                 filename=results_filename)



# =============================================================================
# analyze and show results
# =============================================================================
## get simulation of best candidate
sim = get_best_candidate(eo_dict, iteration=-1, verbose=True)


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







