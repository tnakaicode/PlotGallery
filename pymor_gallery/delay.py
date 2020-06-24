#!/usr/bin/env python
# coding: utf-8
#This file is part of the pyMOR project (http://www.pymor.org).
#Copyright 2013-2020 pyMOR developers and contributors. All rights reserved.
#License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)
# # Create heat equation model

# In[ ]:


import numpy as np
import scipy.linalg as spla
import scipy.sparse as sps
import matplotlib.pyplot as plt

from pymor.basic import *
from pymor.models.iosys import LinearDelayModel
from pymor.reductors.interpolation import DelayBHIReductor, TFBHIReductor


# In[ ]:


p = InstationaryProblem(
    StationaryProblem(
        domain=LineDomain([0.,1.], left='robin', right='robin'),
        diffusion=ConstantFunction(1., 1),
        robin_data=(ConstantFunction(1., 1), ExpressionFunction('(x[...,0] < 1e-10) * 1.', 1)),
        outputs=(('l2_boundary', ExpressionFunction('(x[...,0] > (1 - 1e-10)) * 1.', 1)),)
    ),
    ConstantFunction(0., 1),
    T=3.
)

fom, _ = discretize_instationary_cg(p, diameter=1/100, nt=100)


# In[ ]:


lti = fom.to_lti()


# # Add delayed feedback from output to input

# In[ ]:


tau = 1.
g = 5.
Atau = sps.coo_matrix(([g], ([0], [lti.order - 1])), (lti.order, lti.order)).tocsc()
Atau = NumpyMatrixOperator(Atau, source_id=lti.solution_space.id, range_id=lti.solution_space.id)
td_lti = LinearDelayModel(lti.A, (Atau,), (tau,), lti.B, lti.C, E=lti.E)
print(td_lti)


# In[ ]:


fig, ax = plt.subplots()
w = np.logspace(-1, 2.5, 500)
td_lti.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the FOM')



# # Unstructured Hermite interpolation

# In[ ]:


interp = TFBHIReductor(td_lti)


# In[ ]:


r = 3
sigma = np.logspace(0, 1, r)
sigma = np.concatenate((1j * sigma, -1j * sigma))
b = td_lti.input_space.ones(2 * r)
c = td_lti.output_space.ones(2 * r)

rom = interp.reduce(sigma, b, c)
err_rom = td_lti - rom


# In[ ]:


fig, ax = plt.subplots()
td_lti.mag_plot(w, ax=ax)
rom.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the FOM and ROM')



# In[ ]:


fig, ax = plt.subplots()
err_rom.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the error')



# # Delay-preserving reduction by Hermite interpolation

# In[ ]:


delay_interp = DelayBHIReductor(td_lti)


# In[ ]:


td_rom = delay_interp.reduce(sigma, b, c)
err_td_rom = td_lti - td_rom


# In[ ]:


fig, ax = plt.subplots()
td_lti.mag_plot(w, ax=ax)
rom.mag_plot(w, ax=ax)
td_rom.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the FOM and ROMs')



# In[ ]:


fig, ax = plt.subplots()
err_rom.mag_plot(w, ax=ax, color='tab:orange')
err_td_rom.mag_plot(w, ax=ax, color='tab:green')
ax.set_title('Magnitude plot of the errors')

plt.show()
