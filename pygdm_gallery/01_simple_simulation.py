# encoding: utf-8
from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields
from pyGDM2 import core
from pyGDM2 import visu

## --- alternatively use new API:
# from pyGDM2 import fields_py as fields
# from pyGDM2 import core_py as core

## --- simulation initialization ---
## structure: sphere of 120nm radius,
## constant dielectric function,
## placed in vacuum
step = 20
geometry = structures.sphere(step, R=6, mesh='cube')
material = materials.dummy(2.0)
norm = structures.get_normalization(mesh='cube')
n1 = n2 = 1.0

struct = structures.struct(step, geometry, material, n1,n2, norm)

## incident field: plane wave, 400nm, lin. pol.
field_generator = fields.planewave
wavelengths = [400]
kwargs = dict(theta=0.0, kSign=-1)
efield = fields.efield(field_generator, 
               wavelengths=wavelengths, kwargs=kwargs)

## create simulation object
sim = core.simulation(struct, efield)


## --- run the simulation ---
core.scatter(sim)


## --- plot the near-field inside the sphere ---
## using first (of one) field-config (=index 0)
visu.vectorfield_by_fieldindex(sim, 0, projection='XY')
visu.vectorfield_by_fieldindex(sim, 0, projection='XZ')
visu.vectorfield_by_fieldindex(sim, 0, projection='YZ')

