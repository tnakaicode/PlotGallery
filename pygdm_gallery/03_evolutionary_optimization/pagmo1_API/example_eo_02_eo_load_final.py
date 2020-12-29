# encoding: utf-8
"""
Created on May 6, 2017

@author: P. R. Wiecha

Example script demonstrating `pyGDM2.EO`:
    load best candidate of evolutionary optimizaton of plasmonic 
    nanostructure geometry for directional scattering

"""



import numpy as np
import matplotlib.pyplot as plt



from pyGDM2 import linear
from pyGDM2 import tools
from pyGDM2 import visu

from pyGDM2.EO.tools import get_best_candidate, get_best_candidate_f_x







## --- optimization file locations
results_folder = 'eo_out'
results_suffix = 'test_eo'




## --- reload and plot farfield intensity
N = 1
for i in range(1, N+1)[::-1]:    # reload and plot last N iterations
    
    ## --- load best candidate
    sim = get_best_candidate(results_folder, results_suffix, iteration=-1*i,
                             verbose=True)
    #tools.print_sim_info(sim)
    
    f, x =get_best_candidate_f_x(results_folder, results_suffix, iteration=-1*i)
    
    ## --- calculate farfield pattern
    tetalist, philist, I_sc, I_tot, I0 = linear.farfield(sim, field_index=0,
                                    r=10000, tetamin=0, tetamax=np.pi/2., 
                                    Nteta=18, Nphi=36)
#                                    Nteta=3, Nphi=5)
    
    
    ## --- plot
    plt.figure(figsize=(9,4))
    
    
    plt.subplot(121, aspect="equal")
    NF_imagX = tools.get_field_as_list_by_fieldindex(sim, 0).T[ [0,1,2,3] ]
    NF_imagX[3] = np.angle(NF_imagX[3].imag) * 180./np.pi
    
    plt.scatter(NF_imagX[0], NF_imagX[1], c = NF_imagX[3], cmap='bwr', marker='s')
    plt.colorbar(label=r'phase of $E_x$ (deg)')
    plt.clim([0, 180])
    
    
    
    plt.subplot(122, polar=True)
    visu.farfield_pattern_2D(tetalist, philist, I_sc, show=False)
    plt.colorbar()
    
    plt.show()











