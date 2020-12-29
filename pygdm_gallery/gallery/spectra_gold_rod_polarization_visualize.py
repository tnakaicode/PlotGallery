
# coding: utf-8

# Tutorial: Calculating Spectra
# =================
# This is an example how to calculate spectra from pyGDM simulations.
# 
# We start again by loading the pyGDM modules that we are going to use:

# In[1]:


## --- Load the pyGDM modules 
from pyGDM2 import structures
from pyGDM2 import materials
from pyGDM2 import fields
from pyGDM2 import core
from pyGDM2 import linear
from pyGDM2 import visu
from pyGDM2 import tools

## --- we will use numpy as well
import numpy as np


# Setting up the simulation
# ----------------------------

# In[2]:


## --- we will use again sphere of R=60nm, this time made of gold
## --- for demonstration purpose we will discretize rather coarse
step = 20
geometry = structures.sphere(step, R=3, mesh='cube')
norm = structures.get_normalization(mesh='cube')
material = materials.gold()
n1 = n2 = 1.0

struct = structures.struct(step, geometry, material, n1,n2, norm)


## --- we use again a plane wave
field_generator = fields.planewave
## --- this time however, we want to calculate a whole spectrum.
## --- we use numpy's *linspace* to get a list of linearly 
## --- spaced wavelengths
wavelengths = np.linspace(400, 1000, 30)
## --- let's furthermore simulate three linear polarizations
kwargs = dict(theta=[0, 45, 90], kSign=[-1])

efield = fields.efield(field_generator, 
               wavelengths=wavelengths, kwargs=kwargs)


## --- define the numerical experiment
sim = core.simulation(struct, efield)


# Run the simulation
# --------------------
# 
# **Note:** The output of *scatter* can be turned off by passing "verbose=False"


# Simulation with polarization dependent response
# -----------------------------------
# 
# Finally, let's try what happens if we use a non-symmetric structure which should have an optical response that varies with the incident polarization angle.

# In[12]:


## --- rectangular wire with otherwise same configuration as above
geometry = structures.rect_wire(step, L=20, W=4, H=3)
struct = structures.struct(step, geometry, material, n1,n2, norm)

## --- same spectrum as above but with a lot more polarization angles
kwargs = dict(theta=np.linspace(0, 90, 31), kSign=[-1])
efield = fields.efield(field_generator, 
               wavelengths=wavelengths, kwargs=kwargs)

## --- define the numerical experiment
sim_polarizations = core.simulation(struct, efield)

## --- run the simulation
E = core.scatter(sim_polarizations)


# In[13]:
import matplotlib.pyplot as plt

## --- get the spectra-configurations
spectra_kwargs = tools.get_possible_field_params_spectra(sim_polarizations)

## --- plot scattering for all configs (--> diff. polarizations)
colors = plt.cm.Blues(np.linspace(0.3, 1.0, len(spectra_kwargs)))
for i, field_kwargs in enumerate(spectra_kwargs):
    wl, spec0 = tools.calculate_spectrum(sim_polarizations, i, linear.extinct)

    lab = ''
    if i in [0, len(spectra_kwargs)/2, len(spectra_kwargs)-1]:
        lab = field_kwargs['theta']
    plt.plot(wl, spec0.T[1], color=colors[i], label=lab)

plt.legend(loc='best')
plt.xlabel("wavelength (nm)")
plt.ylabel("scattering cross section (nm^2)")
plt.title("polarization dependent scattering from gold nano-rod", fontsize=13)

plt.tight_layout()
plt.savefig("spectra_gold_rod_polarization.png", dpi=150)
plt.show()


# The different shades of blue indicate the different incident linear polarizations from light blue (zero degrees, parallel to the rod) to dark blue (90 degrees, perpendicular to the rod)
