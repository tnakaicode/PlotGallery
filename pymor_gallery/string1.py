#!/usr/bin/env python
# coding: utf-8
# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2020 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)
# # String equation example

# ## Analytic problem formulation
#
# We consider a vibrating string on the segment $[0, 1]$, fixed on both sides, with input $u$ and output $\tilde{y}$ in the middle:
# $$
# \begin{align*}
#     \partial_{tt} \xi(z, t) + d \partial_t \xi(z, t) - k \partial_{zz} \xi(z, t) & = \delta(z - \tfrac{1}{2}) u(t), & 0 < z < 1,\ t > 0, \\
#     \partial_z \xi(0, t) & = 0, & t > 0, \\
#     \partial_z \xi(1, t) & = 0, & t > 0, \\
#     \tilde{y}(t) & = \xi(1/2, t), & t > 0.
# \end{align*}
# $$
#
# ## Semidiscretized formulation
#
# Using the finite volume method on the equidistant mesh $0 = z_1 < z_2 < \ldots < z_{n + 1} = 1$, where $n = 2 n_2 - 1$, we obtain the semidiscretized formulation:
# $$
# \begin{align*}
#     \ddot{x}_i(t) + d \dot{x}_i(t) - k \frac{x_{i - 1}(t) - 2 x_i(t) + x_{i + 1}(t)}{h^2} & = \frac{1}{h} \delta_{i, n_2} u(t), & i = 1, 2, 3, \ldots, n - 1, n, \\
#     x_0(t) & = 0, \\
#     x_{n + 1}(t) & = 0, \\
#     y(t) & = x_{n_2}(t),
# \end{align*}
# $$
# where $h = \frac{1}{n}$, $x_i(t) \approx \int_{z_i}^{z_{i + 1}} \xi(z, t) \, \mathrm{d}z$, and $y(t) \approx \tilde{y}(t)$.
#
# Separating cases $i = 1$ and $i = n$ in the first equation, we find:
# $$
# \begin{alignat*}{7}
#     \ddot{x}_1(t) & + d \dot{x}_1(t) && && + 2 k n^2 x_1(t) && - k n^2 x_2(t) && = 0, \\
#     \ddot{x}_i(t) & + d \dot{x}_i(t) && - k n^2 x_{i - 1}(t) && + 2 k n^2 x_i(t) && - k n^2 x_{i + 1}(t) && = n \delta_{i, n_2} u(t), && \quad i = 2, 3, \ldots, n - 1, \\
#     \ddot{x}_n(t) & + d \dot{x}_n(t) && - k n^2 x_{n - 1}(t) && + 2 k n^2  x_n(t) && && = 0, \\
#     && && && && y(t) & = x_{n_2}(t).
# \end{alignat*}
# $$

# ## Import modules


import numpy as np
import scipy.sparse as sps
import matplotlib.pyplot as plt

from pymor.core.config import config
from pymor.models.iosys import SecondOrderModel
from pymor.reductors.bt import BTReductor
from pymor.reductors.h2 import IRKAReductor
from pymor.reductors.sobt import (SOBTpReductor, SOBTvReductor, SOBTpvReductor, SOBTvpReductor,
                                  SOBTfvReductor, SOBTReductor)
from pymor.reductors.sor_irka import SORIRKAReductor

from pymor.core.logger import set_log_levels
set_log_levels({'pymor.algorithms.gram_schmidt.gram_schmidt': 'WARNING'})


# ## Assemble $M$, $D$, $K$, $B$, $C_p$


n2 = 50
n = 2 * n2 - 1  # dimension of the system

d = 10  # damping
k = 0.01   # stiffness

M = sps.eye(n, format='csc')

E = d * sps.eye(n, format='csc')

K = sps.diags([n * [2 * k * n ** 2],
               (n - 1) * [-k * n ** 2],
               (n - 1) * [-k * n ** 2]],
              [0, -1, 1],
              format='csc')

B = np.zeros((n, 1))
B[n2 - 1, 0] = n

Cp = np.zeros((1, n))
Cp[0, n2 - 1] = 1


# ## Second-order system


so_sys = SecondOrderModel.from_matrices(M, E, K, B, Cp)
print(so_sys)


poles = so_sys.poles()
fig, ax = plt.subplots()
ax.plot(poles.real, poles.imag, '.')
ax.set_title('System poles')
plt.show()


w = np.logspace(-4, 2, 200)
fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the full model')
plt.show()


psv = so_sys.psv()
vsv = so_sys.vsv()
pvsv = so_sys.pvsv()
vpsv = so_sys.vpsv()
fig, ax = plt.subplots(2, 2, figsize=(12, 8), sharey=True)
ax[0, 0].semilogy(range(1, len(psv) + 1), psv, '.-')
ax[0, 0].set_title('Position singular values')
ax[0, 1].semilogy(range(1, len(vsv) + 1), vsv, '.-')
ax[0, 1].set_title('Velocity singular values')
ax[1, 0].semilogy(range(1, len(pvsv) + 1), pvsv, '.-')
ax[1, 0].set_title('Position-velocity singular values')
ax[1, 1].semilogy(range(1, len(vpsv) + 1), vpsv, '.-')
ax[1, 1].set_title('Velocity-position singular values')
plt.show()


print(f'H_2-norm of the full model:    {so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(f'H_inf-norm of the full model:  {so_sys.hinf_norm():e}')
print(f'Hankel-norm of the full model: {so_sys.hankel_norm():e}')


# ## Position Second-Order Balanced Truncation (SOBTp)


r = 5
sobtp_reductor = SOBTpReductor(so_sys)
rom_sobtp = sobtp_reductor.reduce(r)


poles_rom_sobtp = rom_sobtp.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sobtp.real, poles_rom_sobtp.imag, '.')
ax.set_title("SOBTp reduced model's poles")
plt.show()


err_sobtp = so_sys - rom_sobtp
print(
    f'SOBTp relative H_2-error:    {err_sobtp.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOBTp relative H_inf-error:  {err_sobtp.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOBTp relative Hankel-error: {err_sobtp.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sobtp.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOBTp reduced model')
plt.show()


fig, ax = plt.subplots()
err_sobtp.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOBTp error system')
plt.show()


# ## Velocity Second-Order Balanced Truncation (SOBTv)


r = 5
sobtv_reductor = SOBTvReductor(so_sys)
rom_sobtv = sobtv_reductor.reduce(r)


poles_rom_sobtv = rom_sobtv.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sobtv.real, poles_rom_sobtv.imag, '.')
ax.set_title("SOBTv reduced model's poles")
plt.show()


err_sobtv = so_sys - rom_sobtv
print(
    f'SOBTv relative H_2-error:    {err_sobtv.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOBTv relative H_inf-error:  {err_sobtv.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOBTv relative Hankel-error: {err_sobtv.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sobtv.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOBTv reduced model')
plt.show()


fig, ax = plt.subplots()
err_sobtv.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOBTv error system')
plt.show()


# ## Position-Velocity Second-Order Balanced Truncation (SOBTpv)


r = 5
sobtpv_reductor = SOBTpvReductor(so_sys)
rom_sobtpv = sobtpv_reductor.reduce(r)


poles_rom_sobtpv = rom_sobtpv.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sobtpv.real, poles_rom_sobtpv.imag, '.')
ax.set_title("SOBTpv reduced model's poles")
plt.show()


err_sobtpv = so_sys - rom_sobtpv
print(
    f'SOBTpv relative H_2-error:    {err_sobtpv.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOBTpv relative H_inf-error:  {err_sobtpv.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOBTpv relative Hankel-error: {err_sobtpv.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sobtpv.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOBTpv reduced model')
plt.show()


fig, ax = plt.subplots()
err_sobtpv.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOBTpv error system')
plt.show()


# ## Velocity-Position Second-Order Balanced Truncation (SOBTvp)


r = 5
sobtvp_reductor = SOBTvpReductor(so_sys)
rom_sobtvp = sobtvp_reductor.reduce(r)


poles_rom_sobtvp = rom_sobtvp.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sobtvp.real, poles_rom_sobtvp.imag, '.')
ax.set_title("SOBTvp reduced model's poles")
plt.show()


err_sobtvp = so_sys - rom_sobtvp
print(
    f'SOBTvp relative H_2-error:    {err_sobtvp.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOBTvp relative H_inf-error:  {err_sobtvp.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOBTvp relative Hankel-error: {err_sobtvp.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sobtvp.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOBTvp reduced model')
plt.show()


fig, ax = plt.subplots()
err_sobtvp.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOBTvp error system')
plt.show()


# ## Free-Velocity Second-Order Balanced Truncation (SOBTfv)


r = 5
sobtfv_reductor = SOBTfvReductor(so_sys)
rom_sobtfv = sobtfv_reductor.reduce(r)


poles_rom_sobtfv = rom_sobtfv.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sobtfv.real, poles_rom_sobtfv.imag, '.')
ax.set_title("SOBTfv reduced model's poles")
plt.show()


err_sobtfv = so_sys - rom_sobtfv
print(
    f'SOBTfv relative H_2-error:    {err_sobtfv.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOBTfv relative H_inf-error:  {err_sobtfv.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOBTfv relative Hankel-error: {err_sobtfv.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sobtfv.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOBTfv reduced model')
plt.show()


fig, ax = plt.subplots()
err_sobtfv.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOBTfv error system')
plt.show()


# ## Second-Order Balanced Truncation (SOBT)


r = 5
sobt_reductor = SOBTReductor(so_sys)
rom_sobt = sobt_reductor.reduce(r)


poles_rom_sobt = rom_sobt.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sobt.real, poles_rom_sobt.imag, '.')
ax.set_title("SOBT reduced model's poles")
plt.show()


err_sobt = so_sys - rom_sobt
print(f'SOBT relative H_2-error:    {err_sobt.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOBT relative H_inf-error:  {err_sobt.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOBT relative Hankel-error: {err_sobt.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sobt.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOBT reduced model')
plt.show()


fig, ax = plt.subplots()
err_sobt.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOBT error system')
plt.show()


# ## Balanced Truncation (BT)


r = 5
bt_reductor = BTReductor(so_sys.to_lti())
rom_bt = bt_reductor.reduce(r)


poles_rom_bt = rom_bt.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_bt.real, poles_rom_bt.imag, '.')
ax.set_title("BT reduced model's poles")
plt.show()


err_bt = so_sys - rom_bt
print(f'BT relative H_2-error:    {err_bt.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'BT relative H_inf-error:  {err_bt.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'BT relative Hankel-error: {err_bt.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_bt.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and BT reduced model')
plt.show()


fig, ax = plt.subplots()
err_bt.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the BT error system')
plt.show()


# ## Iterative Rational Krylov Algorithm (IRKA)


r = 5
irka_reductor = IRKAReductor(so_sys.to_lti())
rom_irka = irka_reductor.reduce(r)


fig, ax = plt.subplots()
ax.semilogy(irka_reductor.conv_crit, '.-')
ax.set_title('IRKA convergence criterion')
plt.show()


poles_rom_irka = rom_irka.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_irka.real, poles_rom_irka.imag, '.')
ax.set_title("IRKA reduced model's poles")
plt.show()


err_irka = so_sys - rom_irka
print(f'IRKA relative H_2-error:    {err_irka.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'IRKA relative H_inf-error:  {err_irka.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'IRKA relative Hankel-error: {err_irka.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_irka.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and IRKA reduced model')
plt.show()


fig, ax = plt.subplots()
err_irka.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the IRKA error system')
plt.show()


# ## Second-Order Iterative Rational Krylov Algorithm (SOR-IRKA)


r = 5
sor_irka_reductor = SORIRKAReductor(so_sys)
rom_sor_irka = sor_irka_reductor.reduce(r)


fig, ax = plt.subplots()
ax.semilogy(sor_irka_reductor.conv_crit, '.-')
ax.set_title('SOR-IRKA convergence criterion')
plt.show()


poles_rom_sor_irka = rom_sor_irka.poles()
fig, ax = plt.subplots()
ax.plot(poles_rom_sor_irka.real, poles_rom_sor_irka.imag, '.')
ax.set_title("SOR-IRKA reduced model's poles")
plt.show()


err_sor_irka = so_sys - rom_sor_irka
print(
    f'SOR-IRKA relative H_2-error:    {err_sor_irka.h2_norm() / so_sys.h2_norm():e}')
if config.HAVE_SLYCOT:
    print(
        f'SOR-IRKA relative H_inf-error:  {err_sor_irka.hinf_norm() / so_sys.hinf_norm():e}')
print(
    f'SOR-IRKA relative Hankel-error: {err_sor_irka.hankel_norm() / so_sys.hankel_norm():e}')


fig, ax = plt.subplots()
so_sys.mag_plot(w, ax=ax)
rom_sor_irka.mag_plot(w, ax=ax, linestyle='dashed')
ax.set_title('Magnitude plot of the full and SOR-IRKA reduced model')
plt.show()


fig, ax = plt.subplots()
err_sor_irka.mag_plot(w, ax=ax)
ax.set_title('Magnitude plot of the SOR-IRKA error system')
plt.show()
