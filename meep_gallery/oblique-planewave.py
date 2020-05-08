#!/usr/bin/env python
# coding: utf-8

# # Planewaves in Homogeneous Media

# The eigenmode source can also be used to launch [planewaves](https://en.wikipedia.org/wiki/Plane_wave) in homogeneous media. The dispersion relation for a planewave is ω=|$\vec{k}$|/$n$ where ω is the angular frequency of the planewave and $\vec{k}$ its wavevector; $n$ is the refractive index of the homogeneous medium. This example demonstrates launching planewaves in a uniform medium with $n$ of 1.5 at three rotation angles: 0°, 20°, and 40°. Bloch-periodic boundaries via the `k_point` are used and specified by the wavevector $\vec{k}$. PML boundaries are used only along the x-direction.

# First, we'll load our necesarry modules:

# In[1]:


import meep as mp
import numpy as np
import matplotlib.pyplot as plt


# Next, we'll create a function we can call multiple times that runs the simulation for different rotation angles:

# In[2]:


def run_sim(rot_angle = 0):

    resolution = 50 # pixels/μm

    cell_size = mp.Vector3(14,10,0)

    pml_layers = [mp.PML(thickness=2,direction=mp.X)]

    fsrc = 1.0 # frequency of planewave (wavelength = 1/fsrc)

    n = 1.5 # refractive index of homogeneous material
    default_material = mp.Medium(index=n)

    k_point = mp.Vector3(fsrc*n).rotate(mp.Vector3(z=1), rot_angle)

    sources = [mp.EigenModeSource(src=mp.ContinuousSource(fsrc),
                                  center=mp.Vector3(),
                                  size=mp.Vector3(y=10),
                                  direction=mp.AUTOMATIC if rot_angle == 0 else mp.NO_DIRECTION,
                                  eig_kpoint=k_point,
                                  eig_band=1,
                                  eig_parity=mp.EVEN_Y+mp.ODD_Z if rot_angle == 0 else mp.ODD_Z,
                                  eig_match_freq=True)]

    sim = mp.Simulation(cell_size=cell_size,
                        resolution=resolution,
                        boundary_layers=pml_layers,
                        sources=sources,
                        k_point=k_point,
                        default_material=default_material,
                        symmetries=[mp.Mirror(mp.Y)] if rot_angle == 0 else [])

    sim.run(until=100)
    
    plt.figure(dpi=100)
    sim.plot2D(fields=mp.Ez)
    plt.show()


# Next we'll iterate over three rotation angles and plot their steady-state fields profiles. Residues of the backward-propagating waves due to the discretization are slightly visible.

# In[3]:


for rot_angle in np.radians([0,20,40]):
    run_sim(rot_angle)


# Note that this example involves a `ContinuousSource` for the time profile. For a pulsed source, the oblique planewave is incident at a given angle for only a *single* frequency component of the source. This is a fundamental feature of FDTD simulations and not of Meep per se. Thus, to simulate an incident planewave at multiple angles for a given frequency ω, you will need to do separate simulations involving different values of $\vec{k}$ (`k_point`) since each set of ($\vec{k}$,ω) specifying the Bloch-periodic boundaries and the frequency of the source will produce a different angle of the planewave. For more details, refer to Section 4.5 ("Efficient Frequency-Angle Coverage") in [Chapter 4](https://arxiv.org/abs/1301.5366) ("Electromagnetic Wave Source Conditions") of [Advances in FDTD Computational Electrodynamics: Photonics and Nanotechnology](https://www.amazon.com/Advances-FDTD-Computational-Electrodynamics-Nanotechnology/dp/1608071707).
