#!/usr/bin/env python
# coding: utf-8

# # Third Harmonic Generation

# In this example, we consider wave propagation through a simple 1d nonlinear medium with a non-zero Kerr susceptibility $\chi^{(3)}$. See also Materials and Units and Nonlinearity. We send in a narrow-band pulse at a frequency $\omega$, and because of the nonlinearity we also get a signal at a frequency $3\omega$.
#
# Since this is a 1d calculation, we could implement it via a 2d cell of `Vector3(S,0,0)`, specifying periodic boundary conditions in the `y` direction. However, this is slightly inefficient since the `y` periodic boundaries are implemented internally via extra "ghost pixels" in the `y` direction. Instead, Meep has special support for 1d simulations in the `z` direction. To use this, we must explicitly set dimensions to 1, and in that case we can only use $E_x$ (and $D_x$) and $H_y$ field components. This involves no loss of generality because of the symmetry of the problem.
#
# First, we'll load the necessary modules:

# In[1]:


import meep as mp
import numpy as np
from matplotlib import pyplot as plt
# get_ipython().run_line_magic('matplotlib', 'notebook')


# Next, we'll define some parameters of our simulation:

# In[2]:


sz = 100              # size of cell in z direction
fcen = 1 / 3.0        # center frequency of source
df = fcen / 20.0      # frequency width of source
amp = 1               # amplitude of source
k = 10**-5            # Kerr susceptibility
dpml = 1.0            # PML thickness


# Now, to define our cell, we'll do:

# In[3]:


dimensions = 1
cell = mp.Vector3(0, 0, sz)
pml_layers = mp.PML(dpml)
resolution = 20


# Note that this will only put PMLs at the $\pm z$ boundaries.
#
# In this case, we're going to fill the entire computational cell with the nonlinear medium, so we don't need to use any objects. We can just use the special `default_material` which is ordinarily vacuum:

# In[4]:


default_material = mp.Medium(index=1, chi3=k)


# Now, our source will be a Gaussian pulse of $J_x$ just next to the $−z$ PML layer. Since this is a nonlinear calculation, we may want to play with the amplitude of the current/field, so we set the amplitude property explicitly to our parameter `amp`, above.

# In[5]:


sources = mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ex,
                    center=mp.Vector3(0, 0, -0.5 * sz + dpml), amplitude=amp)


# We'll want the frequency spectrum at the $+z$ end of the computational cell. In a linear problem, we normally look at the spectrum over the same frequency range as our source, because other frequencies are zero. In this case, however, we will look from `fcen/2` to `4*fcen`, to be sure that we can see the third-harmonic frequency.

# In[6]:


nfreq = 400
fmin = fcen / 2.0
fmax = fcen * 4

sim = mp.Simulation(cell_size=cell,
                    geometry=[],
                    sources=[sources],
                    boundary_layers=[pml_layers],
                    default_material=default_material,
                    resolution=resolution,
                    dimensions=dimensions)

trans = sim.add_flux(0.5 * (fmin + fmax), fmax - fmin, nfreq,
                     mp.FluxRegion(mp.Vector3(0, 0, 0.5 * sz - dpml - 0.5)))


# Finally, we'll run the sources, plus additional time for the field to decay at the flux plane, and output the flux spectrum:

# In[7]:


sim.run(until_after_sources=mp.stop_when_fields_decayed(
        50, mp.Ex, mp.Vector3(0, 0, 0.5 * sz - dpml - 0.5), 1e-6))


# In a linear calculation, we normalize the transmission against some reference spectrum, but in this case there is no obvious normalization so we will just plot the raw data. To do so, we'll pull the frequency points using `get_flux_freqs()` and the corrensponding spectra using `get_flux_freqs()`.

# In[8]:


freqs = mp.get_flux_freqs(trans)
spectra = mp.get_fluxes(trans)

plt.figure(dpi=150)
plt.semilogy(freqs, spectra)
plt.grid(True)
plt.xlabel('Frequency')
plt.ylabel('Transmitted Power (a.u.)')
plt.show()


# We next want to see what happens as we slowly increase our nonlinearity term ($\chi^{(3)}$). We'll wrap our routine in a function and parameterize it so that we can quickly loop over the various nonlinearities.
#
# It is also interesting to have a more detailed look at the dependence of the power at $\omega$ and $3\omega$ as a function of $\chi^{(3)}$ and the current amplitude. We could, of course, interpolate the flux spectrum above to get the desired frequencies, but it is easier just to add two more flux regions to Meep and request exactly the desired frequency components. We'll add the additional fluxes to our function:

# In[9]:


def run_chi3(k_pow, amp=1):
    k = 10**k_pow
    default_material = mp.Medium(index=1, chi3=k)

    sources = mp.Source(mp.GaussianSource(fcen, fwidth=df), component=mp.Ex,
                        center=mp.Vector3(0, 0, -0.5 * sz + dpml), amplitude=amp)

    sim = mp.Simulation(cell_size=cell,
                        geometry=[],
                        sources=[sources],
                        boundary_layers=[pml_layers],
                        default_material=default_material,
                        resolution=resolution,
                        dimensions=dimensions)

    trans = sim.add_flux(0.5 * (fmin + fmax), fmax - fmin, nfreq,
                         mp.FluxRegion(mp.Vector3(0, 0, 0.5 * sz - dpml - 0.5)))

    # Single frequency point at omega
    trans1 = sim.add_flux(fcen, 0, 1,
                          mp.FluxRegion(mp.Vector3(0, 0, 0.5 * sz - dpml - 0.5)))

    # Singel frequency point at 3omega
    trans3 = sim.add_flux(3 * fcen, 0, 1,
                          mp.FluxRegion(mp.Vector3(0, 0, 0.5 * sz - dpml - 0.5)))

    sim.run(until_after_sources=mp.stop_when_fields_decayed(
        50, mp.Ex, mp.Vector3(0, 0, 0.5 * sz - dpml - 0.5), 1e-6))

    omega_flux = mp.get_fluxes(trans1)
    omega3_flux = mp.get_fluxes(trans3)
    freqs = mp.get_flux_freqs(trans)
    spectra = mp.get_fluxes(trans)

    return freqs, spectra, omega_flux, omega3_flux


# We'll now loop over various nonlinearities to see what effect this has on our frequency response.

# In[10]:


k_pow = [-3, -2, -1, 0]
freqs = []
spectra = []
for k_iter in k_pow:
    freqs_iter, spectra_iter, omega_flux, omega3_flux = run_chi3(k_iter)
    spectra.append(spectra_iter)
    # Each iteration will simulate over the same frequencies, so just remember the last set.
    freqs = freqs_iter


# In[11]:


plt.figure(dpi=150)
plt.semilogy(freqs, np.array(spectra).T)
plt.grid(True)
plt.xlabel('Frequency')
plt.ylabel('Transmitted Power (a.u.)')
plt.legend(["$\chi^{{(3)}} = 10^{{{}}}$".format(i) for i in k_pow])
plt.show()


# For small values of $\chi^{(3)}$, we see a peak from our source at $\omega=1/3$ and another peak precisely at the third-harmonic frequency $3\oemega=1$. As the $\chi^{(3)}$ gets larger, frequency-mixing within the peaks causes them to broaden, and finally for $\chi^{(3)}=1$ we start to see a noisy, broad-spectrum transmission due to the phenomenon of _modulation instability_. Notice also that at around $10^{−13}$ the data looks weird; this is probably due to our finite simulation time, imperfect absorbing boundaries, etcetera. We haven't attempted to analyze it in detail for this case.
#
# Now, we can look specifically at our frequencies of interest. We'll run a quick simulation for a linear medium. We'll measure the PSD at $\omega$ and use this as a calibration factor for much larger nonlinearities.

# In[12]:


_, _, omega_flux_cal, omega3_flux_cal = run_chi3(-16)
print("Omega: {}, 3Omega: {}".format(omega_flux_cal[0], omega3_flux_cal[0]))


# That is, the linear transmission is 225.25726603587026 at $\omega$, so we'll loop through several nonlinearities, divide by this value, and plot the fractional transmission at $\omega$ and $3\omega$ as a function of $\chi1^{(3)}$ on a log-log scale.

# In[13]:


pts = np.linspace(-6, 0, 20)
_, _, omega_psd, omega3_psd = zip(*[run_chi3(k_iter) for k_iter in pts])


# In[14]:


quad = (10 ** pts) ** 2

plt.figure(dpi=150)
plt.loglog(10 ** pts, np.array(omega_psd) /
           omega_flux_cal[0], 'o-', label='$\omega$')
plt.loglog(10 ** pts, np.array(omega3_psd) /
           omega_flux_cal[0], 'o-', label='$3\omega$')
plt.loglog(10**pts, quad, 'k', label='quadratic line')
plt.grid(True)
plt.xlabel('$\chi^{(3)}$')
plt.ylabel('Transmission/ Incident Power')
plt.legend()
plt.show()


# As can be shown from coupled-mode theory or, equivalently, follows from Fermi's golden rule, the third-harmonic power must go as the square of $\chi^{(3)}$ as long as the nonlinearity is weak (i.e. in the first Born approximation limit, where the $\omega$ source is not depleted significantly). This is precisely what we see on the above graph, where the slope of the black line indicates an exact quadratic dependence, for comparison. Once the nonlinearity gets strong enough, however, this approximation is no longer valid and the dependence is complicated.
#
# Finally, we note that increasing the current amplitude by a factor of $F$ or the Kerr susceptibility $\chi^{(3)}$ by a factor $F^3$ should generate the same third-harmonic power in the weak nonlinearity approximation. And indeed, we see:

# In[15]:


_, _, omega_flux_1, omega3_flux_1 = run_chi3(-3, 1)
_, _, omega_flux_2, omega3_flux_2 = run_chi3(-6, 10)

print('-------------------------------')
print("Difference between powers: {}%".format(
    abs(omega3_flux_1[0] - omega3_flux_2[0]) / omega3_flux_1[0] * 100))


# which have third-harmonic powers differing by about 1%.
