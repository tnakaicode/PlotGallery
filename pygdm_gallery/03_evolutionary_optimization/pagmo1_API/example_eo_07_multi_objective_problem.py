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
from pyGDM2 import tools

from pyGDM2 import core

from pyGDM2.EO.models import RectangularAntenna, CrossAntenna
from pyGDM2.EO.core import do_eo


from PyGMO import algorithm



#==============================================================================
# Implement a simple problem: Maximize 2x scattering efficiency
#==============================================================================
from pyGDM2.EO.problems import BaseProblem

class ownMultiObjectiveProblem(BaseProblem):
    """Problem to maximize scattering efficiency (Q_sc) of nano-structure at two wavelengths"""
    
    def __init__(self, N_dim=9999, model=None, nthreads=1):
        """constructor"""
        ## init base problem for two objective functions
        super(self.__class__, self).__init__(N_dim, model, N_objectives=2, nthreads=nthreads)
        
    
    def objective_function(self, params):
        """evaluate directionality ratio
        """
        self.model.generate_structure(params)
        
        ## --- GDM simulation and cross-section calculation
        core.scatter(self.model.sim, verbose=0)
        
        
        ## --- calculate scattering efficiency 
        ## take first and first or last field config (e.g. two crossed polarizations / two wavelength)
        i_field1 = 0 
        i_field2 = len(self.sim.efield.wavelengths)*len(self.sim.efield.kwargs_permutations) - 1
        
        ext_cs1, sca_cs1, abs_cs1 = linear.extinct(self.model.sim, i_field1)
        ext_cs2, sca_cs2, abs_cs2 = linear.extinct(self.model.sim, i_field2)
        geom_cs = tools.get_geometric_cross_section(self.model.sim)
        
        ## --- index 1: extinction cross-section ("0":extinction, "2":absorption)
        return [ float(sca_cs1/geom_cs), float(sca_cs2/geom_cs) ]


    def human_readable_extra(self):
        return "\n\tMaximization of scattering cross section"





if __name__ == '__main__':
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
    kwargs = dict(theta = [0, 90])            # 2 polarizations
    wavelengths = [800, 1200]                 # 2 wavelengths
    efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)
    
    
    ## ---------- Simulation initialization
    sim = core.simulation(struct, efield)
    
    
    #==============================================================================
    # setup evolutionary optimization
    #==============================================================================
    ## --- output folder and file-names
    results_folder = 'eo_out'
    results_suffix = 'test_MO_problem'
    
    ## --- structure model and optimization problem
    limits_W   = [2, 20]
    limits_L   = [2, 20] 
    limits_pos = [-1, 1]
    height = 3
    model = CrossAntenna(sim, limits_W, limits_L, limits_pos, height)

    problem_dimension = model.get_dim()
    problem = ownMultiObjectiveProblem(problem_dimension, model)
    
    
    ## --- algorithm configuration
    algo = algorithm.sms_emoa(gen=20, m=0.1)  # multi-objective algorithm

    islands = 1             # number of islands ( > 1: multi-processing)
    population = 40         # individuals per island
    
    ## --- stop criteria - this should be considerably larger for "real" problems
    max_time = 600         # seconds
    max_iter = 50          # max. iterations
    max_nonsuccess = 30    # max. consecutive iterations without improvement
    
    
    
    #==============================================================================
    # run evolution
    #==============================================================================
    #do_eo(results_folder, results_suffix, problem)    # run with default params
    do_eo(results_folder, results_suffix,
          problem, algo, 
          islands, population,
          max_time, max_iter, max_nonsuccess, 
          n_report=10,
          ## --- flags
          runtime_plotting=True,
          save_each_generation=False,
          verbose=True)
    
    
    
    
    
    
