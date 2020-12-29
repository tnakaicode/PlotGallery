# encoding: utf-8
import numpy as np
import matplotlib.pyplot as plt

from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core
from pyGDM2 import visu
from pyGDM2 import tools
from pyGDM2 import linear



# =============================================================================
# gold and silicon blocks
# =============================================================================
## --------------- Setup structure
mesh = 'cube'
step = 20.0

## block 1: gold
geom1 = structures.rect_wire(step, L=10,H=3,W=4, mesh=mesh)
mat1 = len(geom1)*[materials.gold()]

## block 2: silicon. Move Y by width of block1
geom2 = structures.rect_wire(step, L=10,H=3,W=4, mesh=mesh)
geom2.T[1] += 4*step
mat2 = len(geom2)*[materials.silicon()]

## block 3: gold. Move Y by widths of block1 and block2
geom3 = structures.rect_wire(step, L=10,H=3,W=4, mesh=mesh)
geom3.T[1] += 8*step
mat3 = len(geom3)*[materials.gold()]


## put together the two blocks (list of coordinate AND list of materials)
geometry = np.concatenate([geom1, geom2, geom3])
material = mat1 + mat2 + mat3



## constant environment
n1, n2 = 1.0, 1.0  
struct = structures.struct(step, geometry, material, n1,n2, structures.get_normalization(mesh))

## incident field
field_generator = fields.planewave
kwargs = dict(theta=0)
wavelengths = [500]
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)


## simulation initialization
sim = core.simulation(struct, efield)


## --------------- run scatter simulation
efield = core.scatter(sim, verbose=True)

## ------------- plot
## plot geometry and real-part of E-field
plt.subplot(aspect='equal')
visu.structure(sim, show=0)
visu.vectorfield_by_fieldindex(sim, 0, show=0)
plt.tight_layout()
plt.savefig("multimaterial_AuSiAu.png")
plt.show()



#%%
# =============================================================================
# graded refractive index structure
# =============================================================================
## ------------- Setup structure
mesh = 'cube'
step = 20.0
geo = structures.rect_wire(step, L=40, H=5, W=5, mesh=mesh)

## graded material, refindex increasing from 1 to 4 (from left to right)
material = []
value_for_plotting = []
for pos in geo:
    ## grade from 1.0 to 4.0
    n = 1.0 + 3*(pos[0] - geo.T[0].min()) / (geo.T[0].max()-geo.T[0].min())
    material.append(materials.dummy(n))
    value_for_plotting.append(n)              # helper list for plotting of index grading



#%%
## constant environment
n1, n2 = 1.0, 1.0  
struct = structures.struct(step, geo, material, n1,n2, structures.get_normalization(mesh))

## incident field
field_generator = fields.planewave        # planwave excitation
kwargs = dict(theta = [90])              # several polarizations
wavelengths = [500]                     # one single wavelength
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)

## simulation initialization
sim = core.simulation(struct, efield)



## ------------- run scatter simulation
efield = core.scatter(sim, verbose=True)



## ------------- plot
## plot geometry and real-part of E-field
plt.figure(figsize=(9,3))
plt.subplot(aspect='equal')
sc = plt.scatter(geo.T[0], geo.T[1], c=value_for_plotting)
plt.colorbar(sc, label="refractive index")
visu.vectorfield_by_fieldindex(sim, 0, scale=7.0, vecwidth=0.7, tit='electric field vector inside (real part)', show=False)

plt.ylim(-120,120)
plt.tight_layout()
plt.savefig("multimaterial_graded_index.png")
plt.show()

## nearfield 2 steps above structure
r_probe = tools.generate_NF_map(-600,600,101, -600,600,101, Z0=geo.T[2].max()+2*step)
Es, Et, Bs, Bt = linear.nearfield(sim, 0, r_probe)

visu.structure_contour(sim, color='w', show=0)
visu.vectorfield_color(Es, tit='intenstiy of scattered field outside', show=0)
plt.colorbar(label=r'$|E_s|^2 / |E_0|^2$')
plt.show()


