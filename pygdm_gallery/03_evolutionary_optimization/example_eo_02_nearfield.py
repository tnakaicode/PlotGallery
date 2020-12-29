# encoding: utf-8
"""
Created on June 1, 2017

@author: P. R. Wiecha

"""
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core

from pyGDM2.EO.problems import ProblemNearfield
from pyGDM2.EO.models import RectangularAntenna
from pyGDM2.EO.core import run_eo




#==============================================================================
# Setup pyGDM simulation
#==============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 15
material = materials.gold()        # material: gold
n1, n2 = 1.0, 1.0         # constant environment

## --- Empty dummy-geometry, will be replaced on run-time by EO trial geometries
geometry = []       
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))


## ---------- Setup incident field
field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = [0.0])              # target polarization
wavelengths = [800]                       # target wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## ---------- Simulation initialization
sim = core.simulation(struct, efield)


#==============================================================================
# setup evolutionary optimization
#==============================================================================
## --- structure model and optimizaiton problem
limits_W   = [2, 20]
limits_L   = [2, 20] 
limits_pos = [-500, 500]
height = 3
model = RectangularAntenna(sim, limits_W, limits_L, limits_pos, height)

target = 'E'
r_probe = [-100, 150, 80]
problem = ProblemNearfield(model, r_probe=r_probe, opt_target=target)



## --- filename to save results 
results_filename = 'eo_NF.eo'

## --- size of population
population = 40          # Nr of individuals

## --- stop criteria
max_time = 500           # seconds
max_iter = 30            # max. iterations
max_nonsuccess = 10      # max. consecutive iterations without improvement

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

print("\n\nOptimization finished. Results were saved to 'eo_NF.eo'. " + \
      "For the analysis and plotting of the results, please run the follow-up example script: " + \
      "'example_eo_02b_nearfield_analyze.py'.")


