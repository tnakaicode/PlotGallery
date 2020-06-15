#!/usr/bin/env python
# coding: utf-8

# # Analyzing the Parker Solar Probe flybys
# 
# ## 1. Modulus of the exit velocity, some features of Orbit #2
# 
# First, using the data available in the reports, we try to compute some of the properties of orbit #2. This is not enough to completely define the trajectory, but will give us information later on in the process.

# In[1]:


from astropy import units as u


# In[2]:


T_ref = 150 * u.day
T_ref


# In[3]:


from poliastro.bodies import Earth, Sun, Venus


# In[4]:


k = Sun.k
k


# In[5]:


import numpy as np


# $$ T = 2 \pi \sqrt{\frac{a^3}{\mu}} \Rightarrow a = \sqrt[3]{\frac{\mu T^2}{4 \pi^2}}$$

# In[6]:


a_ref = np.cbrt(k * T_ref ** 2 / (4 * np.pi ** 2)).to(u.km)
a_ref.to(u.au)


# $$ \varepsilon = -\frac{\mu}{r} + \frac{v^2}{2} = -\frac{\mu}{2a} \Rightarrow v = +\sqrt{\frac{2\mu}{r} - \frac{\mu}{a}}$$

# In[7]:


energy_ref = (-k / (2 * a_ref)).to(u.J / u.kg)
energy_ref


# In[8]:


from poliastro.ephem import Ephem
from poliastro.util import norm

from astropy.time import Time


# In[9]:


flyby_1_time = Time("2018-09-28", scale="tdb")
flyby_1_time


# In[10]:


r_mag_ref = norm(Ephem.from_body(Venus, flyby_1_time).rv()[0])
r_mag_ref.to(u.au)


# In[11]:


v_mag_ref = np.sqrt(2 * k / r_mag_ref - k / a_ref)
v_mag_ref.to(u.km / u.s)


# ## 2. Lambert arc between #0 and #1
# 
# To compute the arrival velocity to Venus at flyby #1, we have the necessary data to solve the boundary value problem.

# In[12]:


d_launch = Time("2018-08-11", scale="tdb")
d_launch


# In[13]:


r0, _ = Ephem.from_body(Earth, d_launch).rv()
r1, V = Ephem.from_body(Venus, flyby_1_time).rv()


# In[14]:


r0 = r0[0]
r1 = r1[0]
V = V[0]


# In[15]:


tof = flyby_1_time - d_launch


# In[16]:


from poliastro import iod


# In[17]:


((v0, v1_pre),) = iod.lambert(Sun.k, r0, r1, tof.to(u.s))


# In[18]:


v0


# In[19]:


v1_pre


# In[20]:


norm(v1_pre)


# ## 3. Flyby #1 around Venus
# 
# We compute a flyby using poliastro with the default value of the entry angle, just to discover that the results do not match what we expected.

# In[21]:


from poliastro.threebody.flybys import compute_flyby


# In[22]:


V.to(u.km / u.day)


# In[23]:


h = 2548 * u.km


# In[24]:


d_flyby_1 = Venus.R + h
d_flyby_1.to(u.km)


# In[25]:


V_2_v_, delta_ = compute_flyby(v1_pre, V, Venus.k, d_flyby_1)


# In[26]:


norm(V_2_v_)


# ## 4. Optimization
# 
# Now we will try to find the value of $\theta$ that satisfies our requirements.

# In[27]:


from poliastro.twobody import Orbit


# In[28]:


def func(theta):
    V_2_v, _ = compute_flyby(v1_pre, V, Venus.k, d_flyby_1, theta * u.rad)
    ss_1 = Orbit.from_vectors(Sun, r1, V_2_v, epoch=flyby_1_time)
    return (ss_1.period - T_ref).to(u.day).value


# There are two solutions:

# In[29]:


import matplotlib.pyplot as plt


# In[30]:


theta_range = np.linspace(0, 2 * np.pi)
plt.plot(theta_range, [func(theta) for theta in theta_range])
plt.axhline(0, color="k", linestyle="dashed");


# In[31]:


func(0)


# In[32]:


func(1)


# In[33]:


from scipy.optimize import brentq


# In[34]:


theta_opt_a = brentq(func, 0, 1) * u.rad
theta_opt_a.to(u.deg)


# In[35]:


theta_opt_b = brentq(func, 4, 5) * u.rad
theta_opt_b.to(u.deg)


# In[36]:


V_2_v_a, delta_a = compute_flyby(v1_pre, V[0], Venus.k, d_flyby_1, theta_opt_a)
V_2_v_b, delta_b = compute_flyby(v1_pre, V[0], Venus.k, d_flyby_1, theta_opt_b)


# In[37]:


norm(V_2_v_a)


# In[38]:


norm(V_2_v_b)


# ## 5. Exit orbit
# 
# And finally, we compute orbit #2 and check that the period is the expected one.

# In[39]:


ss01 = Orbit.from_vectors(Sun, r1, v1_pre, epoch=flyby_1_time)
ss01


# The two solutions have different inclinations, so we still have to find out which is the good one. We can do this by computing the inclination over the ecliptic - however, as the original data was in the International Celestial Reference Frame (ICRF), whose fundamental plane is parallel to the Earth equator of a reference epoch, we have change the plane to the Earth **ecliptic**, which is what the original reports use.

# In[40]:


ss_1_a = Orbit.from_vectors(Sun, r1, V_2_v_a, epoch=flyby_1_time)
ss_1_a


# In[41]:


ss_1_b = Orbit.from_vectors(Sun, r1, V_2_v_b, epoch=flyby_1_time)
ss_1_b


# In[42]:


from poliastro.frames import Planes


# In[43]:


ss_1_a.change_plane(Planes.EARTH_ECLIPTIC)


# In[44]:


ss_1_b.change_plane(Planes.EARTH_ECLIPTIC)


# Therefore, **the correct option is the first one**.

# In[45]:


ss_1_a.period.to(u.day)


# In[46]:


ss_1_a.a


# And, finally, we plot the solution:

# In[47]:


from poliastro.plotting import StaticOrbitPlotter

frame = StaticOrbitPlotter(plane=Planes.EARTH_ECLIPTIC)

frame.plot_body_orbit(Earth, d_launch)
frame.plot_body_orbit(Venus, flyby_1_time)
frame.plot(ss01, label="#0 to #1", color="C2")
frame.plot(ss_1_a, label="#1 to #2", color="C3");

plt.show()