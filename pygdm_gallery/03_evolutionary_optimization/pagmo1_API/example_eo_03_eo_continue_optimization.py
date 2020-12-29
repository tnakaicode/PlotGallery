# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    Demonstrate how to continue a formerly ran evolutionary optimizaton. 
    Continuing the example-optimization of plasmonic nanostructure geometry for 
    directional scattering.

"""


from pyGDM2.EO.core import continue_eo



## --- optimization file locations
results_folder = 'eo_out'
results_suffix = 'test_eo'


## --- Continue evolution
continue_eo(results_folder, results_suffix,
            runtime_plotting=False,
            save_each_generation=False)



















