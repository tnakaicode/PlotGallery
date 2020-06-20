#!/usr/bin/env python
# coding: utf-8

# # Toy weather data
# 
# Here is an example of how to easily manipulate a toy weather dataset using
# xarray and other recommended Python libraries:

# In[ ]:


import numpy as np
import pandas as pd
import seaborn as sns

import xarray as xr

np.random.seed(123)

xr.set_options(display_style="html")

times = pd.date_range("2000-01-01", "2001-12-31", name="time")
annual_cycle = np.sin(2 * np.pi * (times.dayofyear.values / 365.25 - 0.28))

base = 10 + 15 * annual_cycle.reshape(-1, 1)
tmin_values = base + 3 * np.random.randn(annual_cycle.size, 3)
tmax_values = base + 10 + 3 * np.random.randn(annual_cycle.size, 3)

ds = xr.Dataset(
    {
        "tmin": (("time", "location"), tmin_values),
        "tmax": (("time", "location"), tmax_values),
    },
    {"time": times, "location": ["IA", "IN", "IL"]},
)

ds


# ## Examine a dataset with pandas and seaborn

# ### Convert to a pandas DataFrame

# In[ ]:


df = ds.to_dataframe()
df.head()


# In[ ]:


df.describe()


# ### Visualize using pandas

# In[ ]:


ds.mean(dim="location").to_dataframe().plot()


# ### Visualize using seaborn

# In[ ]:


sns.pairplot(df.reset_index(), vars=ds.data_vars)


# ## Probability of freeze by calendar month

# In[ ]:


freeze = (ds["tmin"] <= 0).groupby("time.month").mean("time")
freeze


# In[ ]:


freeze.to_pandas().plot()


# ## Monthly averaging

# In[ ]:


monthly_avg = ds.resample(time="1MS").mean()
monthly_avg.sel(location="IA").to_dataframe().plot(style="s-")


# Note that ``MS`` here refers to Month-Start; ``M`` labels Month-End (the last day of the month).

# ## Calculate monthly anomalies

# In climatology, "anomalies" refer to the difference between observations and
# typical weather for a particular season. Unlike observations, anomalies should
# not show any seasonal cycle.

# In[ ]:


climatology = ds.groupby("time.month").mean("time")
anomalies = ds.groupby("time.month") - climatology
anomalies.mean("location").to_dataframe()[["tmin", "tmax"]].plot()


# ## Calculate standardized monthly anomalies

# You can create standardized anomalies where the difference between the
# observations and the climatological monthly mean is
# divided by the climatological standard deviation.

# In[ ]:


climatology_mean = ds.groupby("time.month").mean("time")
climatology_std = ds.groupby("time.month").std("time")
stand_anomalies = xr.apply_ufunc(
    lambda x, m, s: (x - m) / s,
    ds.groupby("time.month"),
    climatology_mean,
    climatology_std,
)

stand_anomalies.mean("location").to_dataframe()[["tmin", "tmax"]].plot()


# ## Fill missing values with climatology

# The ``fillna`` method on grouped objects lets you easily fill missing values by group:

# In[ ]:


# throw away the first half of every month
some_missing = ds.tmin.sel(time=ds["time.day"] > 15).reindex_like(ds)
filled = some_missing.groupby("time.month").fillna(climatology.tmin)
both = xr.Dataset({"some_missing": some_missing, "filled": filled})
both


# In[ ]:


df = both.sel(time="2000").mean("location").reset_coords(drop=True).to_dataframe()
df.head()


# In[ ]:


df[["filled", "some_missing"]].plot()

