#!/usr/bin/env python
# coding: utf-8

# # Working with Multidimensional Coordinates
# 
# Author: [Ryan Abernathey](https://github.com/rabernat)
# 
# Many datasets have _physical coordinates_ which differ from their _logical coordinates_. Xarray provides several ways to plot and analyze such datasets.

# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import pandas as pd
import xarray as xr
import cartopy.crs as ccrs
from matplotlib import pyplot as plt


# As an example, consider this dataset from the [xarray-data](https://github.com/pydata/xarray-data) repository.

# In[ ]:


ds = xr.tutorial.open_dataset('rasm').load()
ds


# In this example, the _logical coordinates_ are `x` and `y`, while the _physical coordinates_ are `xc` and `yc`, which represent the latitudes and longitude of the data.

# In[ ]:


print(ds.xc.attrs)
print(ds.yc.attrs)


# ## Plotting ##
# 
# Let's examine these coordinate variables by plotting them.

# In[ ]:


fig, (ax1, ax2) = plt.subplots(ncols=2, figsize=(14,4))
ds.xc.plot(ax=ax1)
ds.yc.plot(ax=ax2)


# Note that the variables `xc` (longitude) and `yc` (latitude) are two-dimensional scalar fields.
# 
# If we try to plot the data variable `Tair`, by default we get the logical coordinates.

# In[ ]:


ds.Tair[0].plot()


# In order to visualize the data on a conventional latitude-longitude grid, we can take advantage of xarray's ability to apply [cartopy](http://scitools.org.uk/cartopy/index.html) map projections.

# In[ ]:


plt.figure(figsize=(14,6))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_global()
ds.Tair[0].plot.pcolormesh(ax=ax, transform=ccrs.PlateCarree(), x='xc', y='yc', add_colorbar=False)
ax.coastlines()
ax.set_ylim([0,90]);


# ## Multidimensional Groupby ##
# 
# The above example allowed us to visualize the data on a regular latitude-longitude grid. But what if we want to do a calculation that involves grouping over one of these physical coordinates (rather than the logical coordinates), for example, calculating the mean temperature at each latitude. This can be achieved using xarray's `groupby` function, which accepts multidimensional variables. By default, `groupby` will use every unique value in the variable, which is probably not what we want. Instead, we can use the `groupby_bins` function to specify the output coordinates of the group. 

# In[ ]:


# define two-degree wide latitude bins
lat_bins = np.arange(0,91,2)
# define a label for each bin corresponding to the central latitude
lat_center = np.arange(1,90,2)
# group according to those bins and take the mean
Tair_lat_mean = ds.Tair.groupby_bins('xc', lat_bins, labels=lat_center).mean(dim=xr.ALL_DIMS)
# plot the result
Tair_lat_mean.plot()


# The resulting coordinate for the `groupby_bins` operation got the `_bins` suffix appended: `xc_bins`. This help us distinguish it from the original multidimensional variable `xc`.
# 
# **Note**: This group-by-latitude approach does not take into account the finite-size geometry of grid cells. It simply bins each value according to the coordinates at the cell center. Xarray has no understanding of grid cells and their geometry. More precise geographic regridding for Xarray data is available via the [xesmf](https://xesmf.readthedocs.io) package.

# In[ ]:




