#!/usr/bin/env python
# -*- coding: utf-8 -*-

## --- for benchmark: limit openmp to 1 thread (for parallel scipy/numpy routines)
from __future__ import print_function, division

import os
nthreads = 1
os.environ["MKL_NUM_THREADS"] = "{}".format(int(nthreads))
os.environ["NUMEXPR_NUM_THREADS"] = "{}".format(int(nthreads))
os.environ["OMP_NUM_THREADS"] = "{}".format(int(nthreads))


from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields

from pyGDM2 import core

import numpy as np


## --- Note: It is not necessary to load mpi4py within the simulation script, this 
## --- will be done automatically by pyGDM2 prior to the actual MPI-simulation. 
## --- We do it however at this point to do some output to stdout only from 
## --- the master process (rank == 0).
from mpi4py import MPI
rank = MPI.COMM_WORLD.rank



#==============================================================================
# Configure simulation
#==============================================================================
## ---------- Setup structure
mesh = 'cube'
step = 20.0
radius = 3.5
geometry = structures.sphere(step, R=radius, mesh=mesh)
material = materials.dummy(2.0)
n1, n2 = 1.0, 1.0
struct = structures.struct(step, geometry, material, n1,n2, 
                           structures.get_normalization(mesh))

## ---------- Setup incident field
field_generator = fields.planewave
wavelengths = np.linspace(400, 800, 20)
kwargs = dict(theta = [0.0])
efield = fields.efield(field_generator, wavelengths=wavelengths, kwargs=kwargs)

## ---------- Simulation initialization
sim = core.simulation(struct, efield)



#==============================================================================
# Rum the simulation
#==============================================================================
## --- mpi: print in process with rank=0, to avoid flooding of stdout
if rank == 0: 
    print("performing MPI parallel simulation... ")

core.scatter_mpi(sim)

if rank == 0: 
    print("simulation done.")

