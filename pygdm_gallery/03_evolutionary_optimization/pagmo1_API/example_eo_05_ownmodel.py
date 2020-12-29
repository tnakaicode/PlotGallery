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

from pyGDM2.EO.problems import ProblemMaxScat
from pyGDM2.EO.core import do_eo


from PyGMO import algorithm



#==============================================================================
# Implement a simple problem: Maximize scattering cross-section
#==============================================================================
from pyGDM2.EO.models import BaseModel

class ownModel(BaseModel):
    """optimization-model for simple geometry, consisting of one rectangular antenna
    
    Note : 
        The purpose of this model is only for demonstration. A problem with only 
        two free parameters should probably be solved by brute-force (simulation of 
        all possible permutations)
    
    """
    def __init__(self, sim, limits_W, limits_L, height):
        """
        """
        ## --- init basemodel with simulation instance
        super(self.__class__, self).__init__(sim)
        
        ## --- width and length limits for rectrangular antenna
        self.limits_W = limits_W
        self.limits_L = limits_L
        
        ## --- fixed parameters
        self.height = height    # height of rectangular antenna
        
        ## --- init with random values. `set_step`and `random_structure` are 
        ##     defined in `BaseModel`
        self.set_step(self.sim.struct.step)
        self.random_structure()
    
    def get_dim(self):
        """two free parameters: width / length"""
        return 2
    
    def get_bounds(self):
        """Return lower and upper boundaries for parameters as required by pyGMO models"""
        self.lbnds = [self.limits_W[0], self.limits_L[0]]
        self.ubnds = [self.limits_W[1], self.limits_L[1]]
        
        return self.lbnds, self.ubnds
    
    def generate_structure(self, params):
        """generate the structure"""
        ## --- order of `params` must correspond to boundary order defined by `get_bounds`
        W, L = params[0], params[1]
        
        from pyGDM2 import structures
        geometry = structures.rectwire(self.sim.struct.step, L, self.height, W)
        
        ## -- set new structure-geometry (`set_structure` is a `BaseModel` function)
        self.set_structure(geometry)

















if __name__ == '__main__':
    #==============================================================================
    # Setup pyGDM part
    #==============================================================================
    ## ---------- Setup structure
    mesh = 'cube'
    step = 15
    material = materials.dummy(2.0)    # material: constant and real dielectric function
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
    results_suffix = 'test_own_model_Q_90'
    target = 'Qscat'
    results_suffix = 'test_own_model_Q_800'
    target = 'Qscat'
    
#    results_suffix = 'test_own_model_CS'
#    target = 'CSscat'
    
#    results_suffix = 'test_own_model_CS_800'
#    target = 'CSscat'
    
    
    ## --- structure model and optimizaiton problem
    limits_W = [2, 20]
    limits_L = [2, 20] 
    height = 3
    model = ownModel(sim, limits_W, limits_L, height)
    
    problem_dimension = model.get_dim()
    problem = ProblemMaxScat(problem_dimension, model, opt_target=target)
    
    
    ## --- algorithm configuration
    algo = algorithm.jde(gen=1, memory=True)
    
    islands = 1             # number of islands ( > 1: multi-processing)
    population = 20         # individuals per island
    
    
    ## --- stop criteria
    max_time = 1800         # seconds
    max_iter = 30          # max. iterations
    max_nonsuccess = 10     # max. consecutive iterations without improvement
    
    
    
    
    
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
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
