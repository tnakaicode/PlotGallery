#!/usr/bin/env python
# coding: utf-8

# <h1>Table of Contents<span class="tocSkip"></span></h1>
# <div class="toc"><ul class="toc-item"><li><span><a href="#Compare-weighted-and-unweighted-mean-temperature" data-toc-modified-id="Compare-weighted-and-unweighted-mean-temperature-1"><span class="toc-item-num">1&nbsp;&nbsp;</span>Compare weighted and unweighted mean temperature</a></span><ul class="toc-item"><li><ul class="toc-item"><li><span><a href="#Data" data-toc-modified-id="Data-1.0.1"><span class="toc-item-num">1.0.1&nbsp;&nbsp;</span>Data</a></span></li><li><span><a href="#Creating-weights" data-toc-modified-id="Creating-weights-1.0.2"><span class="toc-item-num">1.0.2&nbsp;&nbsp;</span>Creating weights</a></span></li><li><span><a href="#Weighted-mean" data-toc-modified-id="Weighted-mean-1.0.3"><span class="toc-item-num">1.0.3&nbsp;&nbsp;</span>Weighted mean</a></span></li><li><span><a href="#Plot:-comparison-with-unweighted-mean" data-toc-modified-id="Plot:-comparison-with-unweighted-mean-1.0.4"><span class="toc-item-num">1.0.4&nbsp;&nbsp;</span>Plot: comparison with unweighted mean</a></span></li></ul></li></ul></li></ul></div>

# # Compare weighted and unweighted mean temperature
# 
# 
# Author: [Mathias Hauser](https://github.com/mathause/)
# 
# 
# We use the `air_temperature` example dataset to calculate the area-weighted temperature over its domain. This dataset has a regular latitude/ longitude grid, thus the gridcell area decreases towards the pole. For this grid we can use the cosine of the latitude as proxy for the grid cell area.
# 

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import numpy as np

import xarray as xr


# ### Data
# 
# Load the data, convert to celsius, and resample to daily values

# In[ ]:


ds = xr.tutorial.load_dataset("air_temperature")

# to celsius
air = ds.air - 273.15

# resample from 6-hourly to daily values
air = air.resample(time="D").mean()

air


# Plot the first timestep:

# In[ ]:


projection = ccrs.LambertConformal(central_longitude=-95, central_latitude=45)

f, ax = plt.subplots(subplot_kw=dict(projection=projection))

air.isel(time=0).plot(transform=ccrs.PlateCarree(), cbar_kwargs=dict(shrink=0.7))
ax.coastlines()


# ### Creating weights
# 
# For a for a rectangular grid the cosine of the latitude is proportional to the grid cell area.

# In[ ]:


weights = np.cos(np.deg2rad(air.lat))
weights.name = "weights"
weights


# ### Weighted mean

# In[ ]:


air_weighted = air.weighted(weights)
air_weighted


# In[ ]:


weighted_mean = air_weighted.mean(("lon", "lat"))
weighted_mean


# ### Plot: comparison with unweighted mean
# 
# Note how the weighted mean temperature is higher than the unweighted.

# In[ ]:


weighted_mean.plot(label="weighted")
air.mean(("lon", "lat")).plot(label="unweighted")

plt.legend()

