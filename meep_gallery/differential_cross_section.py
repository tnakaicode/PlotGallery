#!/usr/bin/env python
# coding: utf-8

# # Differential/Radar Cross Section
# 
# As an extension of the [Mie scattering example](https://meep.readthedocs.io/en/latest/Python_Tutorials/Basics/#mie-scattering-of-a-lossless-dielectric-sphere) which involved computing the *scattering* cross section ($\sigma_{scat}$), we will compute the *differential* cross section ($\sigma_{diff}$) which is proportional to the [radar cross section](https://en.wikipedia.org/wiki/Radar_cross-section). Computing $\sigma_{diff}$ in a given direction involves three steps: (1) solve for the [near fields](https://meep.readthedocs.io/en/latest/Python_User_Interface/#near-to-far-field-spectra) on a closed box surrounding the object, (2) from the near fields, compute the far fields at a single point a large distance away (i.e., $R$ ≫  object diameter), and (3) calculate the Poynting flux of the far fields in the outward direction: $F = \hat{r}\cdot\Re[E^* \times H]$. The differential cross section in that direction is $R^2F$ divided by the incident intensity. The radar cross section is simply $\sigma_{diff}$ in the "backwards" direction (i.e., backscattering) multiplied by 4π.
# 
# The scattering cross section can be obtained by integrating the differential cross section over all [spherical angles](https://en.wikipedia.org/wiki/Spherical_coordinate_system):
# 
# <center>
#     $$ \sigma_{scatt} = \int_0^{2\pi} d\phi \int_0^{\pi} \sigma_{diff}(\phi,\theta)\sin(\theta)d\theta $$
# </center>
# 
# In this demonstration, we will verify this expression for the lossless dielectric sphere at a single wavelength by comparing with the analytic theory via PyMieScatt.

# In[1]:


import meep as mp
import numpy as np
import PyMieScatt as ps

r = 1.0  # radius of sphere

frq_cen = 1.0

resolution = 20 # pixels/um

dpml = 0.5
dair = 1.5 # at least 0.5/frq_cen padding between source and near-field monitor

pml_layers = [mp.PML(thickness=dpml)]

s = 2*(dpml+dair+r)
cell_size = mp.Vector3(s,s,s)

# circularly-polarized source with propagation axis along x
# is_integrated=True necessary for any planewave source extending into PML
sources = [mp.Source(mp.GaussianSource(frq_cen,fwidth=0.2*frq_cen,is_integrated=True),
                     center=mp.Vector3(-0.5*s+dpml),
                     size=mp.Vector3(0,s,s),
                     component=mp.Ez),
           mp.Source(mp.GaussianSource(frq_cen,fwidth=0.2*frq_cen,is_integrated=True),
                     center=mp.Vector3(-0.5*s+dpml),
                     size=mp.Vector3(0,s,s),
                     component=mp.Ey,
                     amplitude=1j)]

sim = mp.Simulation(resolution=resolution,
                    cell_size=cell_size,
                    boundary_layers=pml_layers,
                    sources=sources,
                    k_point=mp.Vector3())

box_flux = sim.add_flux(frq_cen, 0, 1,
                        mp.FluxRegion(center=mp.Vector3(x=-2*r),size=mp.Vector3(0,4*r,4*r)))

nearfield_box = sim.add_near2far(frq_cen, 0, 1,
                                 mp.Near2FarRegion(center=mp.Vector3(x=-2*r),size=mp.Vector3(0,4*r,4*r),weight=+1),
                                 mp.Near2FarRegion(center=mp.Vector3(x=+2*r),size=mp.Vector3(0,4*r,4*r),weight=-1),
                                 mp.Near2FarRegion(center=mp.Vector3(y=-2*r),size=mp.Vector3(4*r,0,4*r),weight=+1),
                                 mp.Near2FarRegion(center=mp.Vector3(y=+2*r),size=mp.Vector3(4*r,0,4*r),weight=-1),
                                 mp.Near2FarRegion(center=mp.Vector3(z=-2*r),size=mp.Vector3(4*r,4*r,0),weight=+1),
                                 mp.Near2FarRegion(center=mp.Vector3(z=+2*r),size=mp.Vector3(4*r,4*r,0),weight=-1))

sim.run(until_after_sources=10)

input_flux = mp.get_fluxes(box_flux)[0]
nearfield_box_data = sim.get_near2far_data(nearfield_box)

sim.reset_meep()

n_sphere = 2.0
geometry = [mp.Sphere(material=mp.Medium(index=n_sphere),
                      center=mp.Vector3(),
                      radius=r)]

sim = mp.Simulation(resolution=resolution,
                    cell_size=cell_size,
                    boundary_layers=pml_layers,
                    sources=sources,
                    k_point=mp.Vector3(),
                    geometry=geometry)

nearfield_box = sim.add_near2far(frq_cen, 0, 1,
                                 mp.Near2FarRegion(center=mp.Vector3(x=-2*r),size=mp.Vector3(0,4*r,4*r),weight=+1),
                                 mp.Near2FarRegion(center=mp.Vector3(x=+2*r),size=mp.Vector3(0,4*r,4*r),weight=-1),
                                 mp.Near2FarRegion(center=mp.Vector3(y=-2*r),size=mp.Vector3(4*r,0,4*r),weight=+1),
                                 mp.Near2FarRegion(center=mp.Vector3(y=+2*r),size=mp.Vector3(4*r,0,4*r),weight=-1),
                                 mp.Near2FarRegion(center=mp.Vector3(z=-2*r),size=mp.Vector3(4*r,4*r,0),weight=+1),
                                 mp.Near2FarRegion(center=mp.Vector3(z=+2*r),size=mp.Vector3(4*r,4*r,0),weight=-1))

sim.load_minus_near2far_data(nearfield_box, nearfield_box_data)

sim.run(until_after_sources=100)

npts = 100     # number of points in [0,pi) range of polar angles to sample far fields along semi-circle
angles = np.pi/npts*np.arange(npts)

ff_r = 10000*r # radius of far-field semi-circle

E = np.zeros((npts,3),dtype=np.complex128)
H = np.zeros((npts,3),dtype=np.complex128)
for n in range(npts):
    ff = sim.get_farfield(nearfield_box, ff_r*mp.Vector3(np.cos(angles[n]),0,np.sin(angles[n])))
    E[n,:] = [np.conj(ff[j]) for j in range(3)]
    H[n,:] = [ff[j+3] for j in range(3)]

# compute Poynting flux Pr in the radial direction.  At large r,
# all of the flux is radial so we can simply compute the magnitude of the Poynting vector.
Px = np.real(np.multiply(E[:,1],H[:,2])-np.multiply(E[:,2],H[:,1]))
Py = np.real(np.multiply(E[:,2],H[:,0])-np.multiply(E[:,0],H[:,2]))
Pz = np.real(np.multiply(E[:,0],H[:,1])-np.multiply(E[:,1],H[:,0]))
Pr = np.sqrt(np.square(Px)+np.square(Py)+np.square(Pz))

intensity = input_flux/(4*r)**2
diff_cross_section = ff_r**2 * Pr / intensity
scatt_cross_section_meep = 2*np.pi * np.sum(diff_cross_section * np.sin(angles)) * np.pi/npts # trapezoidal rule integration
scatt_cross_section_theory = ps.MieQ(n_sphere,1000/frq_cen,2*r*1000,asDict=True,asCrossSection=True)['Csca']*1e-6 # units of um^2

print("scatt:, {:.16f}, {:.16f}".format(scatt_cross_section_meep,scatt_cross_section_theory))


# The script is similar to the previous Mie scattering example with the main difference being the replacement of the `add_flux` with `add_near2far` objects. Instead of a linearly-polarized planewave, the source is circularly-polarized so that $\sigma_{diff}$ is invariant with the rotation angle $\phi$ around the axis of the incident direction (i.e., $x$). This way, the far fields need only be sampled with the polar angle $\theta$. A circularly-polarized planewave can be generated by overlapping two linearly-polarized planewaves ($E_y$ and $E_z$) which are 90° out of phase via specifying `amplitude=1j` for one of the two sources. Note, however, that there is no need to use complex fields (by specifying `force_complex_fields=True` in the `Simulation` object) which would double the floating-point memory consumption since only the real part of the source amplitude is used by default. The circularly-polarized source breaks the mirror symmetry which increases the size of the simulation. The size of the near-field monitor box surrounding the sphere is doubled so that it lies *entirely within* the homogeneous air region (a requirement of the `near2far` feature). After the near fields have been obtained for λ = 1 μm the far fields are computed for 100 points along a semi-circle with radius 10,000X that of the dielectric sphere. (Note: any such large radius would give the same $\sigma_{scat}$ to within discretization error). Finally, the scattered cross section is computed by numerically integrating the expression from above using the radial Poynting flux values.
# 
# The Meep results agree well with the analytic theory.
# 
# For `resolution = 20`, the error between the simulated and analytic result is 2.2%.
# ```
# scatt:, 8.1554468215885674, 8.3429545590438750
# ```
# 
# For `resolution = 25`, the error decreases (as expected) to 1.5%.
# ```
# scatt:, 8.2215435272741395, 8.3429545590438750
# ```
