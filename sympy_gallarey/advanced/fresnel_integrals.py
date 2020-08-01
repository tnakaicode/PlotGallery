#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().run_line_magic('pylab', 'inline')


# In[2]:


from sympy import Symbol, fresnels, fresnelc, oo, I, re, im, series, Rational, sin, cos, exp, plot
from sympy.plotting import plot, plot_parametric
from matplotlib.pyplot import figsize


# Plot of the two Fresnel integrals $S(x)$ and $C(x)$

# In[3]:


x = Symbol("x")


# In[4]:


plot(fresnels(x), fresnelc(x), (x, 0, 8))


# The Cornu spiral defined as the parametric curve $u(t),v(t) := C(t), S(t)$

# In[5]:


figsize(8,8)
plot_parametric(fresnelc(x), fresnels(x))


# Compute and plot the leading order behaviour around $x=0$

# In[6]:


ltc = series(fresnelc(x), x, n=2).removeO()
lts = series(fresnels(x), x, n=4).removeO()


# In[7]:


lts, ltc


# In[8]:


figsize(4,4)
plot(fresnels(x), lts, (x, 0, 1))
plot(fresnelc(x), ltc, (x, 0, 1))


# Compute and plot the asymptotic series expansion at $x=\infty$

# In[9]:


# Series expansion at infinity is not implemented yet
#ats = series(fresnels(x), x, oo)
#atc = series(fresnelc(x), x, oo)


# In[10]:


# However we can use the well known values
ats = Rational(1,2) - cos(pi*x**2/2)/(pi*x)
atc = Rational(1,2) + sin(pi*x**2/2)/(pi*x)


# In[11]:


figsize(4,4)
plot(fresnels(x), ats, (x, 6, 8))
plot(fresnelc(x), atc, (x, 6, 8))

Another nice example of a parametric plot
# In[12]:


alpha = Symbol("alpha")
r = 3.0
circ = r*exp(1.0j*alpha)


# In[13]:


figsize(8,8)
plot_parametric(re(fresnelc(circ)), im(fresnelc(circ)), (alpha, 0, 2*pi))


# In[13]:




