#!/usr/bin/env python
# coding: utf-8

# Reading mat files
# =================
# Here are examples of how to read two variables `lat` and `lon` from a mat file called "test.mat".
# 
# = Matlab up to 7.1 =
# mat files created with Matlab up to version 7.1 can be read using the `mio` module part of `scipy.io`. Reading structures (and arrays of structures) is supported, elements are accessed with the same syntax as in Matlab: after reading a structure called e.g. `struct`, its `lat` element can be obtained with `struct.lat`, or `struct.__getattribute__('lat')` if the element name comes from a string.
# 

# In[ ]:


#!python
#!/usr/bin/env python
from scipy.io import loadmat
x = loadmat('test.mat')
lon = x['lon']
lat = x['lat']
# one-liner to read a single variable
lon = loadmat('test.mat')['lon']


# Matlab 7.3 and greater
# ======================
# 
# Beginning at release 7.3 of Matlab, mat files are actually saved using
# the HDF5 format by default (except if you use the -vX flag at save time,
# see in Matlab). These files can be read in Python using, for instance,
# the [PyTables](http://www.pytables.org/moin) or
# [h5py](http://h5py.alfven.org/) package. Reading Matlab structures in
# mat files does not seem supported at this point.

# In[ ]:


#!python
#!/usr/bin/env python
import tables
file = tables.openFile('test.mat')
lon = file.root.lon[:]
lat = file.root.lat[:]
# Alternate syntax if the variable name is in a string
varname = 'lon'
lon = file.getNode('/' + varname)[:]

