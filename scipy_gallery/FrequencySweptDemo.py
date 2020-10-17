#!/usr/bin/env python
# coding: utf-8

# Frequency swept signals
# ======================================================================
# 
# This page demonstrates two functions in scipy.signal for generating
# frequency-swept signals: \`chirp\` and \`sweep\_poly\`.
# 
# Some of these require SciPy 0.8.
# 
# To run the code samples, you will need the following imports:

# In[1]:


import numpy as np
from scipy.signal import chirp, sweep_poly


# Linear Chirp
# ------------
# 
# Sample code:

# In[3]:


t = np.linspace(0, 10, 5001)
w = chirp(t, f0=12.5, f1=2.5, t1=10, method='linear')


# ![](files/attachments/FrequencySweptDemo/chirp_linear.png)
# 
# Quadratic Chirp
# ---------------
# 
# Sample code:

# In[4]:


t = np.linspace(0, 10, 5001)
w = chirp(t, f0=12.5, f1=2.5, t1=10, method='quadratic')


# ![](files/attachments/FrequencySweptDemo/chirp_quadratic.png)
# 
# Sample code using \`vertex\_zero\`:

# In[5]:


t = np.linspace(0, 10, 5001)
w = chirp(t, f0=12.5, f1=2.5, t1=10, method='quadratic', vertex_zero=False)


# ![](files/attachments/FrequencySweptDemo/chirp_quadratic_v0false.png)
# 
# Logarithmic Chirp
# -----------------
# 
# Sample code:

# In[6]:


t = np.linspace(0, 10, 5001)
w = chirp(t, f0=12.5, f1=2.5, t1=10, method='logarithmic')


# ![](files/attachments/FrequencySweptDemo/chirp_logarithmic.png)
# 
# Hyperbolic Chirp
# ----------------
# 
# Sample code:

# In[7]:


t = np.linspace(0, 10, 5001)
w = chirp(t, f0=12.5, f1=2.5, t1=10, method='hyperbolic')


# ![](files/attachments/FrequencySweptDemo/chirp_hyperbolic.png)
# 
# Sweep Poly
# ----------
# 
# Sample code:

# In[9]:


p = np.poly1d([0.05, -0.75, 2.5, 5.0])
t = np.linspace(0, 10, 5001)
w = sweep_poly(t, p)


# ![](files/attachments/FrequencySweptDemo/sweep_poly.png)
# 
# The script that generated the plots is [here](files/attachments/FrequencySweptDemo/chirp_plot.py)
# 
