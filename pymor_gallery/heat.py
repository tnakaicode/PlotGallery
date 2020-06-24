#!/usr/bin/env python
# coding: utf-8
#This file is part of the pyMOR project (http://www.pymor.org).
#Copyright 2013-2020 pyMOR developers and contributors. All rights reserved.
#License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)
# # Heat equation example

# ## Analytic problem formulation
# 
# We consider the heat equation on the segment $[0, 1]$, with dissipation on both sides, heating (input) $u$ on the left, and measurement (output) $\tilde{y}$ on the right:
# $$
# \begin{align*}
#     \partial_t T(z, t) & = \partial_{zz} T(z, t), & 0 < z < 1,\ t > 0, \\
#     \partial_z T(0, t) & = T(0, t) - u(t), & t > 0, \\
#     \partial_z T(1, t) & = -T(1, t), & t > 0, \\
#     \tilde{y}(t) & = T(1, t), & t > 0.
# \end{align*}
# $$
# 

# ## Import modules

# In[ ]:


import numpy as np
import scipy.linalg as spla
import scipy.integrate as spint
import matplotlib.pyplot as plt

from pymor.basic import *
from pymor.core.config import config
from pymor.reductors.h2 import OneSidedIRKAReductor

from pymor.core.logger import set_log_levels
set_log_levels({'pymor.algorithms.gram_schmidt.gram_schmidt': 'WARNING'})


# ## Assemble LTIModel

# ### Discretize problem

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
print(fom)


# ### Visualize solution for constant input of 1

# In[ ]:


fom.visualize(fom.solve())


# ### Convert to LTIModel

# In[ ]:


lti = fom.to_lti()
print(lti)


# ## System analysis

# In[ ]:


poles = lti.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('System poles')



# In[ ]:


w = np.logspace(-2, 3, 100)
fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the full model')



# In[ ]:


hsv = lti.hsv()
fig, ax = plt.subplots()
ax.semilogy(range(1, len(hsv) + 1), hsv, '.-')
ax.set_title('Hankel singular values')



# In[ ]:


print(f'FOM H_2-norm:    {lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'FOM H_inf-norm:  {lti.hinf_norm():e}')
print(f'FOM Hankel-norm: {lti.hankel_norm():e}')


# ## Balanced Truncation (BT)

# In[ ]:


r = 5
bt_reductor = BTReductor(lti)
rom_bt = bt_reductor.reduce(r, tol=1e-5)


# In[ ]:


err_bt = lti - rom_bt
print(f'BT relative H_2-error:    {err_bt.h2_norm() / lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'BT relative H_inf-error:  {err_bt.hinf_norm() / lti.hinf_norm():e}')
print(f'BT relative Hankel-error: {err_bt.hankel_norm() / lti.hankel_norm():e}')


# In[ ]:


poles = rom_bt.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('Poles of the BT reduced model')



# In[ ]:


fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
rom_bt.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and BT reduced model')



# In[ ]:


fig, ax = plt.subplots()
err_bt.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the BT error system')



# ## LQG Balanced Truncation (LQGBT)

# In[ ]:


r = 5
lqgbt_reductor = LQGBTReductor(lti)
rom_lqgbt = lqgbt_reductor.reduce(r, tol=1e-5)


# In[ ]:


err_lqgbt = lti - rom_lqgbt
print(f'LQGBT relative H_2-error:    {err_lqgbt.h2_norm() / lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'LQGBT relative H_inf-error:  {err_lqgbt.hinf_norm() / lti.hinf_norm():e}')
print(f'LQGBT relative Hankel-error: {err_lqgbt.hankel_norm() / lti.hankel_norm():e}')


# In[ ]:


poles = rom_lqgbt.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('Poles of the LQGBT reduced model')



# In[ ]:


fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
rom_lqgbt.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and LQGBT reduced model')



# In[ ]:


fig, ax = plt.subplots()
err_lqgbt.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the LGQBT error system')



# ## Bounded Real Balanced Truncation (BRBT)

# In[ ]:


r = 5
brbt_reductor = BRBTReductor(lti, 0.34)
rom_brbt = brbt_reductor.reduce(r, tol=1e-5)


# In[ ]:


err_brbt = lti - rom_brbt
print(f'BRBT relative H_2-error:    {err_brbt.h2_norm() / lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'BRBT relative H_inf-error:  {err_brbt.hinf_norm() / lti.hinf_norm():e}')
print(f'BRBT relative Hankel-error: {err_brbt.hankel_norm() / lti.hankel_norm():e}')


# In[ ]:


poles = rom_brbt.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('Poles of the BRBT reduced model')



# In[ ]:


fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
rom_brbt.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and BRBT reduced model')



# In[ ]:


fig, ax = plt.subplots()
err_brbt.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the BRBT error system')



# ## Iterative Rational Krylov Algorithm (IRKA)

# In[ ]:


r = 5
irka_reductor = IRKAReductor(lti)
rom_irka = irka_reductor.reduce(r)


# In[ ]:


fig, ax = plt.subplots()
ax.semilogy(irka_reductor.conv_crit, '.-')
ax.set_title('Distances between shifts in IRKA iterations')



# In[ ]:


err_irka = lti - rom_irka
print(f'IRKA relative H_2-error:    {err_irka.h2_norm() / lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'IRKA relative H_inf-error:  {err_irka.hinf_norm() / lti.hinf_norm():e}')
print(f'IRKA relative Hankel-error: {err_irka.hankel_norm() / lti.hankel_norm():e}')


# In[ ]:


poles = rom_irka.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('Poles of the IRKA reduced model')



# In[ ]:


fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
rom_irka.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and IRKA reduced model')



# In[ ]:


fig, ax = plt.subplots()
err_irka.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the IRKA error system')



# ## Two-Sided Iteration Algorithm (TSIA)

# In[ ]:


r = 5
tsia_reductor = TSIAReductor(lti)
rom_tsia = tsia_reductor.reduce(r)


# In[ ]:


fig, ax = plt.subplots()
ax.semilogy(tsia_reductor.conv_crit, '.-')
ax.set_title('Distances between shifts in TSIA iterations')



# In[ ]:


err_tsia = lti - rom_tsia
print(f'TSIA relative H_2-error:    {err_tsia.h2_norm() / lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'TSIA relative H_inf-error:  {err_tsia.hinf_norm() / lti.hinf_norm():e}')
print(f'TSIA relative Hankel-error: {err_tsia.hankel_norm() / lti.hankel_norm():e}')


# In[ ]:


poles = rom_tsia.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('Poles of the TSIA reduced model')



# In[ ]:


fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
rom_tsia.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and TSIA reduced model')



# In[ ]:


fig, ax = plt.subplots()
err_tsia.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the TSIA error system')



# ## One-Sided IRKA

# In[ ]:


r = 5
one_sided_irka_reductor = OneSidedIRKAReductor(lti, 'V')
rom_one_sided_irka = one_sided_irka_reductor.reduce(r)


# In[ ]:


fig, ax = plt.subplots()
ax.semilogy(one_sided_irka_reductor.conv_crit, '.-')
ax.set_title('Distances between shifts in one-sided IRKA iterations')



# In[ ]:


fig, ax = plt.subplots()
osirka_poles = rom_one_sided_irka.poles()
ax.plot(osirka_poles.real, osirka_poles.imag, '.')
ax.set_title('Poles of the one-sided IRKA ROM')



# In[ ]:


err_one_sided_irka = lti - rom_one_sided_irka
print(f'One-sided IRKA relative H_2-error:    {err_one_sided_irka.h2_norm() / lti.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'One-sided IRKA relative H_inf-error:  {err_one_sided_irka.hinf_norm() / lti.hinf_norm():e}')
print(f'One-sided IRKA relative Hankel-error: {err_one_sided_irka.hankel_norm() / lti.hankel_norm():e}')


# In[ ]:


fig, ax = plt.subplots()
lti.mag_plot(w, ax=ax)
rom_one_sided_irka.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and one-sided IRKA reduced model')



# In[ ]:


fig, ax = plt.subplots()
err_one_sided_irka.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the one-sided IRKA error system')



# ## Transfer Function IRKA (TF-IRKA)
# 
# Applying Laplace transformation to the original PDE formulation, we obtain a parametric boundary value problem
# $$
# \begin{align*}
#     s \hat{T}(z, s) & = \partial_{zz} \hat{T}(z, s), \\
#     \partial_z \hat{T}(0, s) & = \hat{T}(0, s) - \hat{u}(s), \\
#     \partial_z \hat{T}(1, s) & = -\hat{T}(1, s), \\
#     \hat{\tilde{y}}(s) & = \hat{T}(1, s),
# \end{align*}
# $$
# where $\hat{T}$, $\hat{u}$, and $\hat{\tilde{y}}$ are respectively Laplace transforms of $T$, $u$, and $\tilde{y}$.
# We assumed the initial condition to be zero ($T(z, 0) = 0$).
# The parameter $s$ is any complex number in the region convergence of the Laplace tranformation.
# 
# Inserting $\hat{T}(z, s) = c_1 \exp\left(\sqrt{s} z\right) + c_2 \exp\left(-\sqrt{s} z\right)$, from the boundary conditions we get a system of equations
# $$
# \begin{align*}
#     \left(\sqrt{s} - 1\right) c_1 - \left(\sqrt{s} + 1\right) c_2 + \hat{u}(s) & = 0, \\
#     \left(\sqrt{s} + 1\right) \exp\left(\sqrt{s}\right) c_1 - \left(\sqrt{s} - 1\right) \exp\left(-\sqrt{s}\right) c_2 & = 0.
# \end{align*}
# $$
# We can solve it using `sympy` and then find the transfer function ($\hat{\tilde{y}}(s) / \hat{u}(s)$).

# In[ ]:


import sympy as sy
sy.init_printing(use_latex=False)

sy_s, sy_u, sy_c1, sy_c2 = sy.symbols('s u c1 c2')

sol = sy.solve([(sy.sqrt(sy_s) - 1) * sy_c1 - (sy.sqrt(sy_s) + 1) * sy_c2 + sy_u,
                (sy.sqrt(sy_s) + 1) * sy.exp(sy.sqrt(sy_s)) * sy_c1 -
                (sy.sqrt(sy_s) - 1) * sy.exp(-sy.sqrt(sy_s)) * sy_c2],
               [sy_c1, sy_c2])

y = sol[sy_c1] * sy.exp(sy.sqrt(sy_s)) + sol[sy_c2] * sy.exp(-sy.sqrt(sy_s))

sy_tf = sy.simplify(y / sy_u)
sy_tf


# Notice that for $s = 0$, the expression is of the form $0 / 0$.

# In[ ]:


sy.limit(sy_tf, sy_s, 0)


# In[ ]:


sy_dtf = sy_tf.diff(sy_s)
sy_dtf


# In[ ]:


sy.limit(sy_dtf, sy_s, 0)


# We can now form the transfer function system.

# In[ ]:


def H(s):
    if s == 0:
        return np.array([[1 / 3]])
    else:
        return np.array([[complex(sy_tf.subs(sy_s, s))]])

def dH(s):
    if s == 0:
        return np.array([[-13 / 54]])
    else:
        return np.array([[complex(sy_dtf.subs(sy_s, s))]])

tf = TransferFunction(lti.input_space, lti.output_space, H, dH)
print(tf)


# Here we compare it to the discretized system, by magnitude plot, $\mathcal{H}_2$-norm, and $\mathcal{H}_2$-distance.

# In[ ]:


tf_lti_diff = tf - lti
fig, ax = plt.subplots()
tf_lti_diff.mag_plot(w, ax=ax)
ax.set_title('Distance between PDE and discretized transfer function')



# In[ ]:


print(f'TF H_2-norm  = {tf.h2_norm():e}')
print(f'LTI H_2-norm = {lti.h2_norm():e}')


# In[ ]:


print(f'TF-LTI relative H_2-distance = {tf_lti_diff.h2_norm() / tf.h2_norm():e}')


# TF-IRKA finds a reduced model from the transfer function.

# In[ ]:


tf_irka_reductor = TFIRKAReductor(tf)
rom_tf_irka = tf_irka_reductor.reduce(r)


# In[ ]:


fig, ax = plt.subplots()
tfirka_poles = rom_tf_irka.poles()
ax.plot(tfirka_poles.real, tfirka_poles.imag, '.')
ax.set_title('Poles of the TF-IRKA ROM')



# Here we compute the $\mathcal{H}_2$-distance from the original PDE model to the TF-IRKA's reduced model and to the IRKA's reduced model.

# In[ ]:


err_tf_irka = tf - rom_tf_irka
print(f'TF-IRKA relative H_2-error = {err_tf_irka.h2_norm() / tf.h2_norm():e}')


# In[ ]:


err_irka_tf = tf - rom_irka
print(f'IRKA relative H_2-error (from TF) = {err_irka_tf.h2_norm() / tf.h2_norm():e}')

plt.show()
