# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    evolutionary optimizaton of plasmonic nanostructure geometry for 
    directional scattering

"""
## --- limit blas to n threads, do this BEFORE loading numpy
import os
nthreads = 2
os.environ["MKL_NUM_THREADS"] = "{}".format(int(nthreads))
os.environ["NUMEXPR_NUM_THREADS"] = "{}".format(int(nthreads))
os.environ["OMP_NUM_THREADS"] = "{}".format(int(nthreads))


import numpy as np
import matplotlib.pyplot as plt


from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core

from pyGDM2.EO import models as eo_models
from pyGDM2.EO import problems as eo_problems
from pyGDM2.EO.core import do_eo


from PyGMO import algorithm


#==============================================================================
# Setup pyGDM part
#==============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 40
#material = materials.dummy(2.0)    # material: constant and real dielectric function
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
results_suffix = 'test_eo'


## --- structure model and optimizaiton problem
model = eo_models.BlockModel(sim, 
                             30, 1,1,1, [-10,10],
                             forbidden=[], symmetric=False)

problem_dimension = model.get_dim()
problem = eo_problems.ProblemDirectivity(problem_dimension, model, nthreads=1)


## --- algorithm configuration
algo = algorithm.jde(gen=1, memory=True)

islands = 1             # number of islands ( > 1: multi-processing)
population = 40         # individuals per island


## --- stop criteria
max_time = 3600         # seconds
max_iter = 200          # max. iterations
max_nonsuccess = 20     # max. consecutive iterations without improvement





#==============================================================================
# run evolution
#==============================================================================
#do_eo(results_folder, results_suffix, problem)    # run with default params
do_eo(results_folder, results_suffix,
      problem, algo, 
      islands, population,
      max_time, max_iter, max_nonsuccess, 
      ## --- flags
      runtime_plotting=0,
      save_each_generation=False,
      verbose=True)



















