#!/usr/bin/env python
# coding: utf-8

# # ROMS Ocean Model Example

# The Regional Ocean Modeling System ([ROMS](http://myroms.org)) is an open source hydrodynamic model that is used for simulating currents and water properties in coastal and estuarine regions. ROMS is one of a few standard ocean models, and it has an active user community.
#
# ROMS uses a regular C-Grid in the horizontal, similar to other structured grid ocean and atmospheric models, and a stretched vertical coordinate (see [the ROMS documentation](https://www.myroms.org/wiki/Vertical_S-coordinate) for more details). Both of these require special treatment when using `xarray` to analyze ROMS ocean model output. This example notebook shows how to create a lazily evaluated vertical coordinate, and make some basic plots. The `xgcm` package is required to do analysis that is aware of the horizontal C-Grid.


import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
#get_ipython().run_line_magic('matplotlib', 'inline')

import xarray as xr


# Load a sample ROMS file. This is a subset of a full model available at
#
#     http://barataria.tamu.edu/thredds/catalog.html?dataset=txla_hindcast_agg
#
# The subsetting was done using the following command on one of the output files:
#
#     #open dataset
#     ds = xr.open_dataset('/d2/shared/TXLA_ROMS/output_20yr_obc/2001/ocean_his_0015.nc')
#
#     # Turn on chunking to activate dask and parallelize read/write.
#     ds = ds.chunk({'ocean_time': 1})
#
#     # Pick out some of the variables that will be included as coordinates
#     ds = ds.set_coords(['Cs_r', 'Cs_w', 'hc', 'h', 'Vtransform'])
#
#     # Select a a subset of variables. Salt will be visualized, zeta is used to
#     # calculate the vertical coordinate
#     variables = ['salt', 'zeta']
#     ds[variables].isel(ocean_time=slice(47, None, 7*24),
#                        xi_rho=slice(300, None)).to_netcdf('ROMS_example.nc', mode='w')
#
# So, the `ROMS_example.nc` file contains a subset of the grid, one 3D variable, and two time steps.

# ### Load in ROMS dataset as an xarray object


# load in the file
ds = xr.tutorial.open_dataset('ROMS_example.nc', chunks={'ocean_time': 1})

# This is a way to turn on chunking and lazy evaluation. Opening with mfdataset, or
# setting the chunking in the open_dataset would also achive this.
ds


# ### Add a lazilly calculated vertical coordinates
#
# Write equations to calculate the vertical coordinate. These will be only evaluated when data is requested. Information about the ROMS vertical coordinate can be found (here)[https://www.myroms.org/wiki/Vertical_S-coordinate]
#
# In short, for `Vtransform==2` as used in this example,
#
# $Z_0 = (h_c \, S + h \,C) / (h_c + h)$
#
# $z = Z_0 (\zeta + h) + \zeta$
#
# where the variables are defined as in the link above.


if ds.Vtransform == 1:
    Zo_rho = ds.hc * (ds.s_rho - ds.Cs_r) + ds.Cs_r * ds.h
    z_rho = Zo_rho + ds.zeta * (1 + Zo_rho / ds.h)
elif ds.Vtransform == 2:
    Zo_rho = (ds.hc * ds.s_rho + ds.Cs_r * ds.h) / (ds.hc + ds.h)
    z_rho = ds.zeta + (ds.zeta + ds.h) * Zo_rho

# needing transpose seems to be an xarray bug
ds.coords['z_rho'] = z_rho.transpose()
ds.salt


# ### A naive vertical slice
#
# Create a slice using the s-coordinate as the vertical dimension is typically not very informative.


ds.salt.isel(xi_rho=50, ocean_time=0).plot()


# We can feed coordinate information to the plot method to give a more informative cross-section that uses the depths. Note that we did not need to slice the depth or longitude information separately, this was done automatically as the variable was sliced.


section = ds.salt.isel(xi_rho=50, eta_rho=slice(0, 167), ocean_time=0)
section.plot(x='lon_rho', y='z_rho', figsize=(15, 6), clim=(25, 35))
plt.ylim([-100, 1])


# ### A plan view
#
# Now make a naive plan view, without any projection information, just using lon/lat as x/y. This looks OK, but will appear compressed because lon and lat do not have an aspect constrained by the projection.


ds.salt.isel(s_rho=-1, ocean_time=0).plot(x='lon_rho', y='lat_rho')


# And let's use a projection to make it nicer, and add a coast.


proj = ccrs.LambertConformal(central_longitude=-92, central_latitude=29)
fig = plt.figure(figsize=(15, 5))
ax = plt.axes(projection=proj)
ds.salt.isel(s_rho=-1, ocean_time=0).plot(x='lon_rho', y='lat_rho',
                                          transform=ccrs.PlateCarree())

coast_10m = cfeature.NaturalEarthFeature('physical', 'land', '10m',
                                         edgecolor='k', facecolor='0.8')
ax.add_feature(coast_10m)
