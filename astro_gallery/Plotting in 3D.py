#!/usr/bin/env python
# coding: utf-8

# # Plotting in 3D

# In[1]:


import numpy as np
import matplotlib.pyplot as plt

from poliastro.constants import J2000
from poliastro.examples import *
from poliastro.plotting import *


# In[2]:


import plotly.io as pio
pio.renderers.default = "notebook_connected"


# In[3]:


#churi.plot(interactive=True, use_3d=True)


# In[4]:


frame = OrbitPlotter3D()

frame.plot(churi)
frame.plot_body_orbit(Earth, J2000)


# In[5]:


frame = OrbitPlotter3D()

frame.plot(molniya)
frame.plot(iss)


# In[6]:


eros = Orbit.from_sbdb("eros")

frame = OrbitPlotter3D()

frame.plot_body_orbit(Earth, J2000)
frame.plot(eros, label="eros")


# In[7]:


from poliastro.ephem import Ephem
from poliastro.util import time_range


# In[8]:


date_launch = time.Time("2011-11-26 15:02", scale="utc").tdb
date_arrival = time.Time("2012-08-06 05:17", scale="utc").tdb

earth = Ephem.from_body(
    Earth, time_range(date_launch, end=date_arrival, periods=50)
)


# In[9]:


frame = OrbitPlotter3D()
frame.set_attractor(Sun)

frame.plot_body_orbit(Earth, J2000, label=Earth)
frame.plot_ephem(earth, label=Earth)


# In[10]:


frame = OrbitPlotter3D()

frame.plot(eros, label="eros")
frame.plot_trajectory(earth.sample(), label=Earth)

plt.show()
