#!/usr/bin/env python
# coding: utf-8

# Function intersections
# ======================================================================
# 
# Find the points at which two given functions intersect
# ------------------------------------------------------
# 
# Consider the example of finding the intersection of a polynomial and a
# line:

# $y_1=x_1^2$
# 
# $y_2=x_2+1$

# In[2]:


from scipy.optimize import fsolve

import numpy as np

def f(xy):
   x, y = xy
   z = np.array([y - x**2, y - x - 1.0])
   return z

fsolve(f, [1.0, 2.0])


# See also: http://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.fsolve.html#scipy.optimize.fsolve
