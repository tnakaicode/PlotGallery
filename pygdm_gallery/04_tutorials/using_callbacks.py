# encoding: utf-8
from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields
from pyGDM2 import core
from pyGDM2 import visu
from pyGDM2 import tools
from pyGDM2 import linear


## --- simulation initialization ---
## structure: dielectric sphere of 60nm radius in vacuum
step = 20
geometry = structures.sphere(step, R=3, mesh='cube')
material = materials.dummy(3.0)
norm = structures.get_normalization(mesh='cube')
n1 = n2 = 1.0

struct = structures.struct(step, geometry, material, n1,n2, norm)

## incident field
field_generator = fields.planewave
wavelengths = [400, 600, 800, 1000, 1200]
kwargs = dict(theta=0.0, kSign=-1)
efield = fields.efield(field_generator, 
               wavelengths=wavelengths, kwargs=kwargs)

## create simulation object
sim = core.simulation(struct, efield)




#%%
## you can make core.scatter call a user-defined function upon every evalutaed
def userdefined_callback_func(callback_dict):
    print("dictionary passed to callback contains:")
    print(callback_dict.keys())
    print("last calculated wavelngth: {}nm".format(callback_dict['wavelength']))
    
    print("calculate nearfield above struct for latest wavelength:")
    sim_tmp = callback_dict['sim']   # unfinished simulation, containing only the so far calculated fields
    r_probe = tools.generate_NF_map(-200, 200, 21, -200, 200, 21, Z0=200)
    fidx = tools.get_closest_field_index(sim_tmp, dict(wavelength=callback_dict['wavelength']))
    Es, Et, Bs, Bt = linear.nearfield(sim, fidx, r_probe)
    visu.vectorfield_color(Et, tit='wl={}nm'.format(callback_dict['wavelength']))
    
    
    if callback_dict['wavelength']<900:
        print ("wavelength<900nm. continue...\n")
        return True   # return True means continue
    ## abort simulation if last wavelength > 900nm
    else:
        print ("\n")
        print ("wl>900nm. abort simulation to demonstrate use of stop condition.")
        return False  # if return False here, core.scatter will stop
    


## --- run the simulation ---
core.scatter(sim, callback=userdefined_callback_func, verbose=False)


