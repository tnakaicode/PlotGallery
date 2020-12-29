# encoding: utf-8
"""
Example script, simulating the coupling of a dipolar emitter to a 
gold splitring resonator.

"""
from __future__ import print_function, division

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import tools
from pyGDM2 import visu

import numpy as np
import matplotlib.pyplot as plt






#==============================================================================
# setup simulation
#==============================================================================
mesh = 'cube'
step = 30.0
geometry = structures.rect_split_ring(step, L1=12,L2=16,H=3,W=3, G=False, mesh=mesh)
material = materials.gold()

n1, n2 = 1.0, 1.0  # constant environment

geometry = structures.center_struct(geometry)
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))



## --- Setup incident field
field_generator = fields.dipole_electric   # light-source: dipolar emitter
kwargs = dict(x0=0, y0=0, z0=1.5*step, 
              mx=[1,0], my=[0,1], mz=0)
wavelengths = [1000.]
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)



## --- Simulation initialization
sim = core.simulation(struct, efield)

tools.print_sim_info(sim, verbose=1)






#%%
#==============================================================================
# run the simulation
#==============================================================================
E = core.scatter(sim, method='LU', verbose=True)
#E = core.scatter(sim, method='cuda', matrix_setup='numba', verbose=True)
#E = core.scatter(sim, method='cuda', matrix_setup='cuda', verbose=True)


## --- farfield pattern ("backfocal plane image")
Nteta=40; Nphi=2*72

teta, phi, I_sc_0, I_tot_0, I0_0 = linear.farfield(
                                sim, field_index=0,   # index 0: dipole || X 
                                tetamin=0, tetamax=np.pi/2., 
                                Nteta=Nteta, Nphi=Nphi)
teta, phi, I_sc_90, I_tot_90, I0_90 = linear.farfield(
                                sim, field_index=3,   # index 3: dipole || Y
                                tetamin=0, tetamax=np.pi/2., 
                                Nteta=Nteta, Nphi=Nphi)





#%%
#==============================================================================
# plot
#==============================================================================
scale_I = 1E16

def conf_polar():
    plt.ylim([0, 90])
    plt.gca().set_xticklabels([])
    plt.gca().set_yticklabels([])


plt.figure()

## --- structure geometry
plt.subplot(131, aspect='equal')
plt.title("structure")
plt.axis('off')

## structure
visu.structure(geometry, color='#c7a800', scale=1, show=False)

bbox = plt.gca().get_window_extent().transformed(plt.gcf().dpi_scale_trans.inverted())
width, height = bbox.width*plt.gcf().dpi, bbox.height*plt.gcf().dpi
               
## dipole position
plt.text(0, 40, r"$\mathbf{p}$", ha='center', va='bottom')
plt.scatter([0], [0], marker='x', linewidth=2, s=20, color='k')

## scale bar
plt.text(120,-330, "100nm", ha='center', va='bottom')
plt.plot([70,170] , [-350,-350], lw=2, color='k', clip_on=False)

geo_dim = 300
plt.xlim([-geo_dim, geo_dim])
plt.ylim([-geo_dim, geo_dim])


## --- pattern for dipole along X
plt.subplot(132, polar=True)
plt.title("$\mathbf{p} \parallel X$", x=0.5, y=1.15)
im = visu.farfield_pattern_2D(teta, phi, I_sc_0*scale_I, degrees=True, show=False)
conf_polar()

plt.colorbar(im, orientation='horizontal', label=r'$|\mathbf{E}|^2$ (a.u.)', shrink=0.75, 
             pad=0.05, aspect=15, ticks=[0, 0.5, 1.0])
plt.clim([0, 1])


## --- pattern for dipole along Y
plt.subplot(133, polar=True)
plt.title("$\mathbf{p} \parallel Y$", x=0.5, y=1.15)
im = visu.farfield_pattern_2D(teta, phi, I_sc_90*scale_I, degrees=True, show=False)
conf_polar()

plt.colorbar(im, orientation='horizontal', label=r'$|\mathbf{E}|^2$ (a.u.)', shrink=0.75, 
             pad=0.05, aspect=15, ticks=[0, 0.05, 0.10, 0.15])
plt.clim([0, 0.15])


plt.tight_layout()
plt.show()



