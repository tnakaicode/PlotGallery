#!/usr/bin/env python
# coding: utf-8

# dbase
# ======================================================================
# 
# > **NOTE**: You may want to use [pandas](http://pandas.pydata.org/) instead of this.
# 
# The [dbase.py](files/attachments/dbase/dbase.0.7.py) class, can be used to
# read/write/summarize/plot time-series data.
# 
# To summarize the functionality:
# 
# 1. data and variable names stored in a dictionary - accessible using variable names
# 2. load/save from/to csv/pickle format, including date information (shelve format to be added)
# 3. plotting and descriptive statistics, with dates if provided
# 4. adding/deleting variables, including trends/(seasonal)dummies
# 5. selecting observations based on dates or other variable values (e.g., > 1/1/2003)
# 6. copying instance data
# 
# Attached also the [dbase_pydoc.txt](files/attachments/dbase/dbase_pydoc.0.2.txt) information for the class.
# 
# Example Usage
# -------------
# 
# To see the class in action download the file and run it (python
# dbase.py). This will create an example data file
# (./dbase\_test\_files/data.csv) that will be processed by the class.
# 
# To import the module:

# In[1]:


import sys
sys.path.append('attachments/dbase')
import dbase


# After running the class you can load the example data using

# In[2]:


data = dbase.dbase("attachments/dbase/data.csv", date = 0)


# In the above command '0' is the index of the column containing dates.
# 
# You can plot series 'b' and 'c' in the file using

# In[3]:


data.dataplot('b','c')


# ![](files/attachments/dbase/ex_plot.0.1.png)
# 
# You get descriptive statistics for series 'a','b', and 'c' by using

# In[4]:


data.info('a','b','c')

