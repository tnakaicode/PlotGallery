#!/usr/bin/env python
# coding: utf-8

# Calculating Seasonal Averages from Timeseries of Monthly Means
# =====
#
# Author: [Joe Hamman](https://github.com/jhamman/)
#
# The data used for this example can be found in the [xarray-data](https://github.com/pydata/xarray-data) repository. You may need to change the path to `rasm.nc` below.
#
# Suppose we have a netCDF or `xarray.Dataset` of monthly mean data and we want to calculate the seasonal average.  To do this properly, we need to calculate the weighted average considering that each month has a different number of days.


#get_ipython().run_line_magic('matplotlib', 'inline')
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib.pyplot as plt


# #### Open the `Dataset`


ds = xr.tutorial.open_dataset('rasm').load()


# #### Now for the heavy lifting:
# We first have to come up with the weights,
# - calculate the month lengths for each monthly data record
# - calculate weights using `groupby('time.season')`
#
# Finally, we just need to multiply our weights by the `Dataset` and sum allong the time dimension.  Creating a `DataArray` for the month length is as easy as using the `days_in_month` accessor on the time coordinate.  The calendar type, in this case `'noleap'`, is automatically considered in this operation.


month_length = ds.time.dt.days_in_month


# Calculate the weights by grouping by 'time.season'.
weights = month_length.groupby('time.season') / \
    month_length.groupby('time.season').sum()

# Test that the sum of the weights for each season is 1.0
np.testing.assert_allclose(weights.groupby(
    'time.season').sum().values, np.ones(4))

# Calculate the weighted average
ds_weighted = (ds * weights).groupby('time.season').sum(dim='time')


# only used for comparisons
ds_unweighted = ds.groupby('time.season').mean('time')
ds_diff = ds_weighted - ds_unweighted


# Quick plot to show the results
notnull = pd.notnull(ds_unweighted['Tair'][0])

fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(14, 12))
for i, season in enumerate(('DJF', 'MAM', 'JJA', 'SON')):
    ds_weighted['Tair'].sel(season=season).where(notnull).plot.pcolormesh(
        ax=axes[i, 0], vmin=-30, vmax=30, cmap='Spectral_r',
        add_colorbar=True, extend='both')

    ds_unweighted['Tair'].sel(season=season).where(notnull).plot.pcolormesh(
        ax=axes[i, 1], vmin=-30, vmax=30, cmap='Spectral_r',
        add_colorbar=True, extend='both')

    ds_diff['Tair'].sel(season=season).where(notnull).plot.pcolormesh(
        ax=axes[i, 2], vmin=-0.1, vmax=.1, cmap='RdBu_r',
        add_colorbar=True, extend='both')

    axes[i, 0].set_ylabel(season)
    axes[i, 1].set_ylabel('')
    axes[i, 2].set_ylabel('')

for ax in axes.flat:
    ax.axes.get_xaxis().set_ticklabels([])
    ax.axes.get_yaxis().set_ticklabels([])
    ax.axes.axis('tight')
    ax.set_xlabel('')

axes[0, 0].set_title('Weighted by DPM')
axes[0, 1].set_title('Equal Weighting')
axes[0, 2].set_title('Difference')

plt.tight_layout()

fig.suptitle('Seasonal Surface Air Temperature', fontsize=16, y=1.02)
plt.show()

# Wrap it into a simple function


def season_mean(ds, calendar='standard'):
    # Make a DataArray with the number of days in each month, size = len(time)
    month_length = ds.time.dt.days_in_month

    # Calculate the weights by grouping by 'time.season'
    weights = month_length.groupby(
        'time.season') / month_length.groupby('time.season').sum()

    # Test that the sum of the weights for each season is 1.0
    np.testing.assert_allclose(weights.groupby(
        'time.season').sum().values, np.ones(4))

    # Calculate the weighted average
    return (ds * weights).groupby('time.season').sum(dim='time')
