#!/usr/bin/env python
# coding: utf-8

# # GRIB Data Example 

# GRIB format is commonly used to disemminate atmospheric model data. With Xarray and the cfgrib engine, GRIB data can easily be analyzed and visualized.

# In[ ]:


import xarray as xr
import matplotlib.pyplot as plt


# To read GRIB data, you can use `xarray.load_dataset`. The only extra code you need is to specify the engine as `cfgrib`.

# In[ ]:


ds = xr.tutorial.load_dataset('era5-2mt-2019-03-uk.grib', engine='cfgrib')


# Let's create a simple plot of 2-m air temperature in degrees Celsius:

# In[ ]:


ds = ds - 273.15
ds.t2m[0].plot(cmap=plt.cm.coolwarm)


# With CartoPy, we can create a more detailed plot, using built-in shapefiles to help provide geographic context:

# In[ ]:


import cartopy.crs as ccrs
import cartopy
fig = plt.figure(figsize=(10,10))
ax = plt.axes(projection=ccrs.Robinson())
ax.coastlines(resolution='10m')
plot = ds.t2m[0].plot(cmap=plt.cm.coolwarm, transform=ccrs.PlateCarree(), cbar_kwargs={'shrink':0.6})
plt.title('ERA5 - 2m temperature British Isles March 2019')


# Finally, we can also pull out a time series for a given location easily:

# In[ ]:


ds.t2m.sel(longitude=0,latitude=51.5).plot()
plt.title('ERA5 - London 2m temperature March 2019')

