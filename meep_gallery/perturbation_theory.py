#!/usr/bin/env python
# coding: utf-8

# Sensitivity Analysis via Perturbation Theory
# --------------------------------------------
#
# For a given mode of the ring resonator, it is often useful to know how sensitive the resonant frequency $\omega$ is to small changes in the ring radius $r$ by computing its derivative $\partial\omega/\partial r$. The gradient is also a useful quantity for shape optimization because it can be paired with fast iterative methods such as [BFGS](https://en.wikipedia.org/wiki/Broyden%E2%80%93Fletcher%E2%80%93Goldfarb%E2%80%93Shanno_algorithm) to find local optima. The "brute-force" approach for computing the gradient is via a finite-difference approximation requiring *two* simulations of the (1) unperturbed [$\omega(r)$] and (2) perturbed [$\omega(r+\Delta r)$] structures. Since each simulation is potentially costly, an alternative approach based on semi analytics is to use [perturbation theory](https://en.wikipedia.org/wiki/Perturbation_theory) to obtain the gradient from the fields of the unperturbed structure. This involves a single simulation and is often more computationally efficient than the brute-force approach although some care is required to set up the calculation properly.  (More generally, [adjoint methods](https://math.mit.edu/~stevenj/18.336/adjoint.pdf) can be used to compute any number of derivatives with a single additional simulation.)
#
# [Pertubation theory for Maxwell equations involving high index-contrast dielectric interfaces](http://math.mit.edu/~stevenj/papers/KottkeFa08.pdf) is reviewed in Chapter 2 of [Photonics Crystals: Molding the Flow of Light, 2nd Edition (2008)](http://ab-initio.mit.edu/book/). The formula (equation 30 on p.19) for the frequency shift $\Delta \omega$ resulting from the displacement of a block of $\varepsilon_1$-material towards $\varepsilon_2$-material by a distance $\Delta h$ (perpendicular to the boundary) is:
#
# <center>
#
# $$ \Delta\omega = -\frac{\omega}{2} \frac{ \iint d^2 \vec{r} \big[ (\varepsilon_1 - \varepsilon_2) |\vec{E}_{\parallel}(\vec{r})|^2 - \big(\frac{1}{\varepsilon_1} - \frac{1}{\varepsilon_2}\big)|\varepsilon\vec{E}_{\perp}|^2\big] \Delta h}{\int d^3\vec{r} \varepsilon(\vec{r})|\vec{E}(\vec{r})|^2} + O(\Delta h^2)$$
#
# </center>
#
# In this expression, $\vec{E}_{\parallel}(\vec{r})$ is the component of $\vec{E}$ that is parallel to the surface, and $\varepsilon\vec{E}_{\perp}$ is the component of $\varepsilon\vec{E}$ that is perpendicular to the surface. These two components are guaranteed to be continuous across an interface between two isotropic dielectric materials. In this demonstration, $\partial\omega/\partial r$ is computed using this formula and the results are validated by comparing with the finite-difference approximation: $[\omega(r+\Delta r)-\omega(r)]/\Delta r$.
#
# There are three parts to the calculation: (1) find the resonant frequency of the unperturbed geometry using a broadband Gaussian source, (2) find the resonant mode profile of the unperturbed geometry using a narrowband source and from these fields compute the gradient via the perturbation-theory formula, and (3) find the resonant frequency of the perturbed geometry and from this compute the gradient using a finite-difference approximation. The perturbation is applied only to the inner and outer ring radii. The ring width is constant. There are two types of modes which are computed in separate simulations using different source polarizations: parallel ($E_z$) and perpendicular ($H_z$) to the interface.

# In[1]:


import meep as mp
import numpy as np

resolution = 100        # pixels/um

perpendicular = False   # perpendicular (Hz) or parallel (Ez) source?

if perpendicular:
    src_cmpt = mp.Hz
    fcen = 0.21         # pulse center frequency
else:
    src_cmpt = mp.Ez
    fcen = 0.17         # pulse center frequency

n = 3.4                 # index of waveguide
w = 1                   # ring width
r = 1                   # inner radius of ring
pad = 4                 # padding between waveguide and edge of PML
dpml = 2                # thickness of PML
m = 5                   # angular dependence

pml_layers = [mp.PML(dpml)]

sr = r + w + pad + dpml        # radial size (cell is from 0 to sr)
# coordinate system is (r,phi,z) instead of (x,y,z)
dimensions = mp.CYLINDRICAL
cell = mp.Vector3(sr)

geometry = [mp.Block(center=mp.Vector3(r + (w / 2)),
                     size=mp.Vector3(w, mp.inf, mp.inf),
                     material=mp.Medium(index=n))]

# find resonant frequency of unperturbed geometry using broadband source

df = 0.2 * fcen           # pulse width (in frequency)

sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df),
                     component=src_cmpt,
                     center=mp.Vector3(r + 0.1))]

sim = mp.Simulation(cell_size=cell,
                    geometry=geometry,
                    boundary_layers=pml_layers,
                    resolution=resolution,
                    sources=sources,
                    dimensions=dimensions,
                    m=m)

h = mp.Harminv(src_cmpt, mp.Vector3(r + 0.1), fcen, df)
sim.run(mp.after_sources(h),
        until_after_sources=100)

frq_unperturbed = h.modes[0].freq

sim.reset_meep()

# unperturbed geometry with narrowband source centered at resonant frequency

fcen = frq_unperturbed
df = 0.05 * fcen

sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df),
                     component=src_cmpt,
                     center=mp.Vector3(r + 0.1))]

sim = mp.Simulation(cell_size=cell,
                    geometry=geometry,
                    boundary_layers=pml_layers,
                    resolution=resolution,
                    sources=sources,
                    dimensions=dimensions,
                    m=m)

sim.run(until_after_sources=100)

deps = 1 - n**2
deps_inv = 1 - 1 / n**2

if perpendicular:
    para_integral = deps * 2 * np.pi * (r * abs(sim.get_field_point(mp.Ep, mp.Vector3(
        r)))**2 - (r + w) * abs(sim.get_field_point(mp.Ep, mp.Vector3(r + w)))**2)
    perp_integral = deps_inv * 2 * np.pi * (-r * abs(sim.get_field_point(mp.Dr, mp.Vector3(
        r)))**2 + (r + w) * abs(sim.get_field_point(mp.Dr, mp.Vector3(r + w)))**2)
    numerator_integral = para_integral + perp_integral
else:
    numerator_integral = deps * 2 * np.pi * (r * abs(sim.get_field_point(mp.Ez, mp.Vector3(
        r)))**2 - (r + w) * abs(sim.get_field_point(mp.Ez, mp.Vector3(r + w)))**2)

denominator_integral = sim.electric_energy_in_box(
    center=mp.Vector3(0.5 * sr), size=mp.Vector3(sr))

perturb_theory_dw_dR = -frq_unperturbed * \
    numerator_integral / (4 * denominator_integral)

sim.reset_meep()

# perturbed geometry with narrowband source

dr = 0.01

sources = [mp.Source(mp.GaussianSource(fcen, fwidth=df),
                     component=src_cmpt,
                     center=mp.Vector3(r + dr + 0.1))]

geometry = [mp.Block(center=mp.Vector3(r + dr + (w / 2)),
                     size=mp.Vector3(w, mp.inf, mp.inf),
                     material=mp.Medium(index=n))]

sim = mp.Simulation(cell_size=cell,
                    geometry=geometry,
                    boundary_layers=pml_layers,
                    resolution=resolution,
                    sources=sources,
                    dimensions=dimensions,
                    m=m)

h = mp.Harminv(src_cmpt, mp.Vector3(r + dr + 0.1), fcen, df)
sim.run(mp.after_sources(h),
        until_after_sources=100)

frq_perturbed = h.modes[0].freq

finite_diff_dw_dR = (frq_perturbed - frq_unperturbed) / dr

print("dwdR:, {} (pert. theory), {} (finite diff.)".format(
    perturb_theory_dw_dR, finite_diff_dw_dR))


# There are three things to note. First, there is a built-in function `electric_energy_in_box` which calculates the integral of $\vec{E}\cdot\vec{D}/2 = \varepsilon|E|^2/2$. This is exactly the integral in the denominator, divided by 2. In cylindrical coordinates $(r,\phi,z)$, the integrand is [multiplied](https://en.wikipedia.org/wiki/Cylindrical_coordinate_system#Line_and_volume_elements) by the circumference $2\pi r$, or equivalently the integral is over an annular volume. Second, for the case involving the $H_z$ source, both parallel ($E_{\parallel}=E_{\phi}$) and perpendicular ($\varepsilon E_{\perp}=D_r$) fields are present which must be included in the numerator as separate terms. Field values anywhere in the grid obtained with `get_field_point` are [automatically interpolated](https://meep.readthedocs.io/en/latest/Introduction/#the-illusion-of-continuity); i.e., no additional post-processing is necessary. Third, when comparing the perturbation-theory result to the finite-difference approximation, there are *two* convergence parameters: the resolution and $\Delta r$. In principle, to demonstrate agreement with perturbation theory, the limit of the resolution should be taken to infinity and *then* the limit of $\Delta r$ to 0. In practice, this can be obtained by doubling the resolution at a given $\Delta r$ until it is sufficiently converged, then halving $\Delta r$ and repeating.
#
# For an $E_z$ source (parallel to the interface), at a resolution of 100 the results are -0.0854469639 (perturbation theory) and -0.0852124909 (finite difference). Doubling the resolution to 200, the results are -0.0854460732 (perturbation theory) and -0.0852115350 (finite difference). Both results have converged to at least five digits. The relative error at resolution 200 is 0.3%. The mode has a $\omega$ of 0.175 and $Q$ of 1800.
#
# For an $H_z$ source (perpendicular to the interface), at a resolution of 100 the results are -0.0805038572 (perturbation theory) and -0.0798087331 (finite difference). Doubling the resolution to 200, the results are -0.0802028346 (perturbation theory) and -0.0798088015 (finite difference). Both results have converged to at least three digits. The relative error at resolution 200 is 0.5%. The error is larger in this case due to the presence of the discontinuous fields at the dielectric interface which are handled by [subpixel smoothing](https://meep.readthedocs.io/en/latest/Subpixel_Smoothing/). The mode has a $\omega$ of 0.208 and $Q$ of 1200.
#
# Finally, as reference, the same calculation can be set up in Cartesian coordinates as a 2d simulation. There is one major difference: the mode produced by a point source in 2d is actually the $\cos(m\phi)$ mode, *not* $\exp(im\phi)$, or equivalently it is the superposition of the $\pm m$ modes. This means that computing the numerator integral does not involve just multiplying the field at a single point on the surface by $2\pi r$ &mdash; rather, it is the integral of $\cos^2(m\phi)$ which gives a factor of 1/2. (For non-circular shapes in 2d, the surface integral must be computed numerically.) The simulation script is in [examples/perturbation_theory_2d.py](https://github.com/NanoComp/meep/blob/master/python/examples/perturbation_theory_2d.py). The results are comparable to the cylindrical coordinate case (a 1d calculation) but the 2d simulation is much slower and less accurate at the same grid resolution.
