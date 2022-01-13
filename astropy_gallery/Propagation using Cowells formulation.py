#!/usr/bin/env python
# coding: utf-8

# # Cowell's formulation
# 
# For cases where we only study the gravitational forces, solving the Kepler's equation is enough to propagate the orbit forward in time. However, when we want to take perturbations that deviate from Keplerian forces into account, we need a more complex method to solve our initial value problem: one of them is **Cowell's formulation**.
# 
# In this formulation we write the two body differential equation separating the Keplerian and the perturbation accelerations:
# 
# $$\ddot{\mathbb{r}} = -\frac{\mu}{|\mathbb{r}|^3} \mathbb{r} + \mathbb{a}_d$$

# <div class="alert alert-info">For an in-depth exploration of this topic, still to be integrated in poliastro, check out <a href="https://github.com/Juanlu001/pfc-uc3m">this Master thesis</a></div>

# <div class="alert alert-info">An earlier version of this notebook allowed for more flexibility and interactivity, but was considerably more complex. Future versions of poliastro and plotly might bring back part of that functionality, depending on user feedback. You can still download the older version <a href="https://github.com/poliastro/poliastro/blob/0.8.x/docs/source/examples/Propagation%20using%20Cowell's%20formulation.ipynb">here</a>.</div>

# ## First example
# 
# Let's setup a very simple example with constant acceleration to visualize the effects on the orbit.

# In[1]:


import numpy as np
from astropy import units as u
from astropy import time

from poliastro.bodies import Earth
from poliastro.twobody import Orbit
from poliastro.twobody.propagation import propagate
from poliastro.examples import iss

from poliastro.twobody.propagation import cowell
from poliastro.plotting import OrbitPlotter3D
from poliastro.util import norm


# In[2]:


import plotly.io as pio
pio.renderers.default = "notebook_connected"


# To provide an acceleration depending on an extra parameter, we can use **closures** like this one:

# In[3]:


accel = 2e-5


# In[4]:


def constant_accel_factory(accel):
    def constant_accel(t0, u, k):
        v = u[3:]
        norm_v = (v[0]**2 + v[1]**2 + v[2]**2)**.5
        return accel * v / norm_v

    return constant_accel


# In[5]:


times = np.linspace(0, 10 * iss.period, 500)
times


# In[6]:


positions = propagate(
    iss,
    time.TimeDelta(times),
    method=cowell,
    rtol=1e-11,
    ad=constant_accel_factory(accel),
)


# And we plot the results:

# In[7]:


frame = OrbitPlotter3D()

frame.set_attractor(Earth)
frame.plot_trajectory(positions, label="ISS")


# ## Error checking

# In[8]:


def state_to_vector(ss):
    r, v = ss.rv()
    x, y, z = r.to(u.km).value
    vx, vy, vz = v.to(u.km / u.s).value
    return np.array([x, y, z, vx, vy, vz])


# In[9]:


k = Earth.k.to(u.km ** 3 / u.s ** 2).value


# In[10]:


rtol = 1e-13
full_periods = 2


# In[11]:


u0 = state_to_vector(iss)
tf = ((2 * full_periods + 1) * iss.period / 2)

u0, tf


# In[12]:


iss_f_kep = iss.propagate(tf, rtol=1e-18)


# In[13]:


r, v = cowell(iss.attractor.k, iss.r, iss.v, [tf] * u.s, rtol=rtol)


# In[14]:


iss_f_num = Orbit.from_vectors(Earth, r[0], v[0], iss.epoch + tf)


# In[15]:


iss_f_num.r, iss_f_kep.r


# In[16]:


assert np.allclose(iss_f_num.r, iss_f_kep.r, rtol=rtol, atol=1e-08 * u.km)
assert np.allclose(iss_f_num.v, iss_f_kep.v, rtol=rtol, atol=1e-08 * u.km / u.s)


# In[17]:


assert np.allclose(iss_f_num.a, iss_f_kep.a, rtol=rtol, atol=1e-08 * u.km)
assert np.allclose(iss_f_num.ecc, iss_f_kep.ecc, rtol=rtol)
assert np.allclose(iss_f_num.inc, iss_f_kep.inc, rtol=rtol, atol=1e-08 * u.rad)
assert np.allclose(iss_f_num.raan, iss_f_kep.raan, rtol=rtol, atol=1e-08 * u.rad)
assert np.allclose(iss_f_num.argp, iss_f_kep.argp, rtol=rtol, atol=1e-08 * u.rad)
assert np.allclose(iss_f_num.nu, iss_f_kep.nu, rtol=rtol, atol=1e-08 * u.rad)


# ## Numerical validation
# 
# According to [Edelbaum, 1961], a coplanar, semimajor axis change with tangent thrust is defined by:
# 
# $$\frac{\operatorname{d}\!a}{a_0} = 2 \frac{F}{m V_0}\operatorname{d}\!t, \qquad \frac{\Delta{V}}{V_0} = \frac{1}{2} \frac{\Delta{a}}{a_0}$$
# 
# So let's create a new circular orbit and perform the necessary checks, assuming constant mass and thrust (i.e. constant acceleration):

# In[18]:


ss = Orbit.circular(Earth, 500 * u.km)
tof = 20 * ss.period

ad = constant_accel_factory(1e-7)

r, v = cowell(ss.attractor.k, ss.r, ss.v, [tof] * u.s, ad=ad)

ss_final = Orbit.from_vectors(Earth, r[0], v[0], ss.epoch + tof)


# In[19]:


da_a0 = (ss_final.a - ss.a) / ss.a
da_a0


# In[20]:


dv_v0 = abs(norm(ss_final.v) - norm(ss.v)) / norm(ss.v)
2 * dv_v0


# In[21]:


np.allclose(da_a0, 2 * dv_v0, rtol=1e-2)


# This means **we successfully validated the model against an extremely simple orbit transfer with approximate analytical solution**. Notice that the final eccentricity, as originally noticed by Edelbaum, is nonzero:

# In[22]:


ss_final.ecc


# ## References
# 
# * [Edelbaum, 1961] "Propulsion requirements for controllable satellites"
