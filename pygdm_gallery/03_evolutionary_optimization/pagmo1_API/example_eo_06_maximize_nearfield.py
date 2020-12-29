# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    Demonstrate how to implement a user-defined problem. 
    The example problem is the maximization of the scattering cross-section
    of a simple plasmonic nano-structure under plane wave illumination with 
    fixed wavelength and linear polarization angle.

"""

import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core

from pyGDM2.EO.problems import ProblemMaxNearfield
from pyGDM2.EO.models import RectangularAntenna
from pyGDM2.EO.core import do_eo


from PyGMO import algorithm



#==============================================================================
# Setup pyGDM part
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
kwargs = dict(theta = [0.0])              # several polarizations
wavelengths = [800]                       # one single wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)



## ---------- Simulation initialization
sim = core.simulation(struct, efield)




#==============================================================================
# setup evolutionary optimization
#==============================================================================
## --- output folder and file-names
results_folder = 'eo_out'
results_suffix = 'test_max_NF_E'


## --- structure model and optimizaiton problem
limits_W   = [2, 20]
limits_L   = [2, 20] 
limits_pos = [-500, 500]
height = 1
model = RectangularAntenna(sim, limits_W, limits_L, limits_pos, height)

target = 'E'
r_probe = [0, 0, 80]
problem_dimension = model.get_dim()
problem = ProblemMaxNearfield(problem_dimension, model, r_probe=r_probe, opt_target=target)


## --- algorithm configuration
algo = algorithm.jde(gen=1, memory=True)

islands = 1             # number of islands ( > 1: multi-processing)
population = 20         # individuals per island


## --- stop criteria
max_time = 3600         # seconds
max_iter = 200          # max. iterations
max_nonsuccess = 30     # max. consecutive iterations without improvement





#==============================================================================
# run evolution
#==============================================================================
#do_eo(results_folder, results_suffix, problem)    # run with default params
do_eo(results_folder, results_suffix,
      problem, algo, 
      islands, population,
      max_time, max_iter, max_nonsuccess, 
      ## --- flags
      runtime_plotting=True,
      save_each_generation=False,
      verbose=True)










