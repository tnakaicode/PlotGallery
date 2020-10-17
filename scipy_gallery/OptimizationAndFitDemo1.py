#!/usr/bin/env python
# coding: utf-8

# Optimization and fit demo
# =========================
# 
# This is a quick example of creating data from several [Bessel
# functions](http://docs.scipy.org/doc/scipy/reference/special.html) and
# finding local maxima, then fitting a curve using some spline functions
# from the
# [scipy.interpolate](http://docs.scipy.org/doc/scipy/reference/interpolate.html)
# module. The [enthought.chaco](http://code.enthought.com/chaco/) package
# and [wxpython](http://www.wxpython.org/) are used for creating the plot.
# [PyCrust](http://wiki.wxpython.org/index.cgi/PyCrust) (which comes with
# wxpython) was used as the python shell.

# In[ ]:


from enthought.chaco.wx import plt
from scipy import arange, optimize, special

plt.figure()
plt.hold()
w = []
z = []
x = arange(0,10,.01)

for k in arange(1,5,.5):
   y = special.jv(k,x)
   plt.plot(x,y)
   f = lambda x: -special.jv(k,x)
   x_max = optimize.fminbound(f,0,6)
   w.append(x_max)
   z.append(special.jv(k,x_max))
   
plt.plot(w,z, 'ro')
from scipy import interpolate
t = interpolate.splrep(w, z, k=3)
s_fit3 = interpolate.splev(x,t)
plt.plot(x,s_fit3, 'g-')
t5 = interpolate.splrep(w, z, k=5)
s_fit5 = interpolate.splev(x,t5)
plt.plot(x,s_fit5, 'y-')


# In[ ]:


#class left

# ![](files/attachments/OptimizationAndFitDemo1/chacoscreenshot.png)
Optimization Example

