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
from pyGDM2 import linear

from pyGDM2 import core

from pyGDM2.EO import models as eo_models
from pyGDM2.EO.core import do_eo


from PyGMO import algorithm



#==============================================================================
# Implement a simple problem: Maximize scattering cross-section
#==============================================================================
from pyGDM2.EO.problems import BaseProblem

class ownProblem(BaseProblem):
    """Problem to maximize scattering cross-section (SCS) of nano-structure"""
    
    def __init__(self, N_dim=9999, model=None, nthreads=1):
        """constructor"""
        super(self.__class__, self).__init__(N_dim, model, nthreads=nthreads)
    
    
    def objective_function(self, params):
        """evaluate directionality ratio
        """
        self.model.generate_structure(params)
        
        ## --- GDM simulation and cross-section calculation
        core.scatter(self.model.sim, verbose=0)
        ext_cs, sca_cs, abs_cs = linear.extinct(self.model.sim, 0)
        
        return float(sca_cs)      


    def human_readable_extra(self):
        return "\n\tMaximization of scattering cross section"







if __name__ == '__main__':
    #==============================================================================
    # Setup pyGDM part
    #==============================================================================
    ## ---------- Setup structure
    mesh = 'cube'
    step = 20
    material = materials.dummy(2.0)    # material: constant and real dielectric function
    material = materials.gold()        # material: gold
    n1, n2 = 1.0, 1.0         # constant environment
    
    ## --- Empty dummy-geometry, will be replaced on run-time by EO trial geometries
    geometry = []       
    
    struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))
    
    
    
    ## ---------- Setup incident field
    field_generator = fields.planewave        # planwave excitation
    kwargs = dict(theta = [0.0])              # several polarizations
    wavelengths = [1200]                       # one single wavelength
    efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)
    
    
    
    ## ---------- Simulation initialization
    sim = core.simulation(struct, efield)
    
    
    
    
    #==============================================================================
    # setup evolutionary optimization
    #==============================================================================
    ## --- output folder and file-names
    results_folder = 'eo_out'
    results_suffix = 'test_own_problem'
    
    
    ## --- structure model and optimizaiton problem
    model = eo_models.BlockModel(sim, 
                                 20, 1,1,1, [-10,10],
                                 forbidden=[], symmetric=False)
    
    problem_dimension = model.get_dim()
    problem = ownProblem(problem_dimension, model)
    
    
    ## --- algorithm configuration
    algo = algorithm.jde(gen=1, memory=True)
    
    islands = 4             # number of islands ( > 1: multi-processing)
    population = 40         # individuals per island
    
    
    ## --- stop criteria
    max_time = 1800         # seconds
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
          runtime_plotting=True,
          save_each_generation=False,
          verbose=True)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
