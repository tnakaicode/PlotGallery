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
from __future__ import print_function, division

import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields
from pyGDM2 import linear
from pyGDM2 import tools

from pyGDM2 import core

from pyGDM2.EO.models import CrossAntenna
from pyGDM2.EO.core import run_eo





#==============================================================================
# Implement a simple problem: Maximize 2x scattering efficiency
#==============================================================================
from pyGDM2.EO.problems import BaseProblem

class ownMultiObjectiveProblem(BaseProblem):
    """maximize scattering efficiency (Q_sc) of nano-structure at two wavelengths"""
    
    def __init__(self, model):
        """
        In the Problem constructor, the constructor of the parent 
        class "BaseProblem" must be called, passing the `model` object.:
        """
        super(self.__class__, self).__init__(model)
        
    
    def objective_function(self, params):
        """calculate the scat. efficiency for 2 incident field configs
        
        This method implements the multi-objective problem: 
        The objective function returns an array with several objective
        function values (the "objective vector").
        Just as in a single-objective scenario, `objective_function` 
        is function of the free parameters `params`.
        
        Use the `field_index` parameter to select the different incident
        field configurations. In this example problem we use the first
        and last available `field_index`.
        
        """
        ## --- generate the structure geometry as function of `params`
        self.model.generate_structure(params)
        
        ## --- GDM simulation and cross-section calculation
        core.scatter(self.model.sim, verbose=0)
        
        ## --- calculate scattering efficiency 
        ##     take first and second last field config 
        ##     (e.g. two crossed polarizations at two wavelengths)
        i_field1 = 0 
        i_field2 = len(self.model.sim.E) - 1
        
        ext_cs1, sca_cs1, abs_cs1 = linear.extinct(self.model.sim, field_index=i_field1)
        ext_cs2, sca_cs2, abs_cs2 = linear.extinct(self.model.sim, field_index=i_field2)
        geom_cs = tools.get_geometric_cross_section(self.model.sim)
        
        ## --- scattering efficieny (scat eff. = scat CS / geometric CS)
        return [ float(sca_cs1/geom_cs), float(sca_cs2/geom_cs) ]





if __name__ == '__main__':
    #==============================================================================
    # Setup pyGDM part
    #==============================================================================
    ## ---------- Setup structure
    mesh = 'cube'
    step = 20
    material = materials.gold()  # structure material
    n1, n2 = 1.0, 1.0            # in vacuum
    
    ## --- Empty dummy-geometry, will be replaced on run-time by EO trial geometries
    geometry = []       
    struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))
    
    
    ## ---------- Setup incident field
    field_generator = fields.planewave        # planwave excitation
    kwargs = dict(theta = [0, 90])            # 2 polarizations
    wavelengths = [600, 1400]                 # 2 wavelengths
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
    limits_pos = []
    height = 3
    model = CrossAntenna(sim, limits_W, limits_L, limits_pos, height)
    
    problem = ownMultiObjectiveProblem(model)
    
    
    ## --- filename to save results 
    results_filename = 'emo_test.eo'
    
    ## --- size of population
    population = 100          # Nr of individuals
    
    ## --- stop criteria
    max_time = 600            # seconds
    max_iter = 50            # max. iterations
    max_nonsuccess = 10      # max. consecutive iterations without improvement
    
    ## --- other config
    generations = 1          # generations to evolve between status reports
    plot_interval = 1
    save_all_generations = True
    
    ##  Use multi-objective algorithm "moead" (decomposition into single obj. DE)
    import pygmo as pg
    algorithm = pg.moead
    algorithm_kwargs = dict(weight_generation='grid', decomposition='bi')  # optional kwargs
    algorithm = pg.maco
    algorithm_kwargs = dict()  # optional kwargs
#    algorithm_kwargs = dict(weight_generation='low discrepancy', decomposition='weighted')  # optional kwargs
#    algorithm_kwargs = dict(neighbours=20, preserve_diversity=False)  # optional kwargs
    
    ## --- "NSGA2" EMO algorithm
#    algorithm = pg.nsga2
#    algorithm_kwargs = dict(m=0.1)  # optional kwarg: 10% mutation chance
    
    
    
    eo_dict = run_eo(problem,
                     population=population,
                     algorithm=algorithm,
                     plot_interval=plot_interval, 
                     generations=generations, 
                     max_time=max_time, max_iter=max_iter, max_nonsuccess=max_nonsuccess,
                     filename=results_filename)
    
    
    
print("\n\nOptimization finished. Results were saved to 'emo_test.eo'. " + \
      "For the analysis and plotting of the results, please run the follow-up example script: " + \
      "'example_eo_03b_multi_objective_analyze.py'.")
    
    
    
    
    
