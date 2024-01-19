import gmsh


def mesh():
    r_core = 10 / 2
    r_cladding = 125 / 2
    r_box = 400 / 2
    x_fiber = -100
    y_fiber = 0

    mesh_fiber = 2
    mesh_box = 4

    gmsh.initialize()
    gmsh.model.add('Scatterer')

    tag_pt_box_center = gmsh.model.geo.addPoint(0, 0, 0, meshSize=mesh_fiber)
    tag_pt_fiber_center = gmsh.model.geo.addPoint(
        x_fiber, y_fiber, 0, meshSize=mesh_fiber)

    tag_pt_core_x0 = gmsh.model.geo.addPoint(
        x_fiber - r_core, y_fiber, 0, meshSize=mesh_fiber)
    tag_pt_core_x1 = gmsh.model.geo.addPoint(
        x_fiber + r_core, y_fiber, 0, meshSize=mesh_fiber)
    tag_pt_core_y0 = gmsh.model.geo.addPoint(
        x_fiber, y_fiber - r_core, 0, meshSize=mesh_fiber)
    tag_pt_core_y1 = gmsh.model.geo.addPoint(
        x_fiber, y_fiber + r_core, 0, meshSize=mesh_fiber)

    tag_circle_cladding_x0 = gmsh.model.geo.addPoint(
        x_fiber - r_cladding, y_fiber, 0, meshSize=mesh_fiber)
    tag_circle_cladding_x1 = gmsh.model.geo.addPoint(
        x_fiber + r_cladding, y_fiber, 0, meshSize=mesh_fiber)
    tag_circle_cladding_y0 = gmsh.model.geo.addPoint(
        x_fiber, y_fiber - r_cladding, 0, meshSize=mesh_fiber)
    tag_circle_cladding_y1 = gmsh.model.geo.addPoint(
        x_fiber, y_fiber + r_cladding, 0, meshSize=mesh_fiber)

    tag_circle_box_x0 = gmsh.model.geo.addPoint(
        -1 * r_box, 0, 0, meshSize=mesh_box)
    tag_circle_box_x1 = gmsh.model.geo.addPoint(r_box, 0, 0, meshSize=mesh_box)
    tag_circle_box_y0 = gmsh.model.geo.addPoint(
        0, -1 * r_box, 0, meshSize=mesh_box)
    tag_circle_box_y1 = gmsh.model.geo.addPoint(0, r_box, 0, meshSize=mesh_box)

    tag_arc_core0 = gmsh.model.geo.addCircleArc(
        tag_pt_core_x1, tag_pt_fiber_center, tag_pt_core_y1)
    tag_arc_core1 = gmsh.model.geo.addCircleArc(
        tag_pt_core_y1, tag_pt_fiber_center, tag_pt_core_x0)
    tag_arc_core2 = gmsh.model.geo.addCircleArc(
        tag_pt_core_x0, tag_pt_fiber_center, tag_pt_core_y0)
    tag_arc_core3 = gmsh.model.geo.addCircleArc(
        tag_pt_core_y0, tag_pt_fiber_center, tag_pt_core_x1)

    tag_arc_cladding0 = gmsh.model.geo.addCircleArc(
        tag_circle_cladding_x1, tag_pt_fiber_center, tag_circle_cladding_y1)
    tag_arc_cladding1 = gmsh.model.geo.addCircleArc(
        tag_circle_cladding_y1, tag_pt_fiber_center, tag_circle_cladding_x0)
    tag_arc_cladding2 = gmsh.model.geo.addCircleArc(
        tag_circle_cladding_x0, tag_pt_fiber_center, tag_circle_cladding_y0)
    tag_arc_cladding3 = gmsh.model.geo.addCircleArc(
        tag_circle_cladding_y0, tag_pt_fiber_center, tag_circle_cladding_x1)

    tag_arc_box0 = gmsh.model.geo.addCircleArc(
        tag_circle_box_x1, tag_pt_box_center, tag_circle_box_y1)
    tag_arc_box1 = gmsh.model.geo.addCircleArc(
        tag_circle_box_y1, tag_pt_box_center, tag_circle_box_x0)
    tag_arc_box2 = gmsh.model.geo.addCircleArc(
        tag_circle_box_x0, tag_pt_box_center, tag_circle_box_y0)
    tag_arc_box3 = gmsh.model.geo.addCircleArc(
        tag_circle_box_y0, tag_pt_box_center, tag_circle_box_x1)

    tag_loop_box = gmsh.model.geo.addCurveLoop(
        [tag_arc_box0, tag_arc_box1, tag_arc_box2, tag_arc_box3])
    tag_loop_core = gmsh.model.geo.addCurveLoop(
        [tag_arc_core0, tag_arc_core1, tag_arc_core2, tag_arc_core3])
    tag_loop_cladding = gmsh.model.geo.addCurveLoop(
        [tag_arc_cladding0, tag_arc_cladding1, tag_arc_cladding2, tag_arc_cladding3])

    tag_surf_air = gmsh.model.geo.addPlaneSurface(
        [tag_loop_box, tag_loop_core, tag_loop_cladding])
    tag_surf_cladding = gmsh.model.geo.addPlaneSurface(
        [tag_loop_cladding, tag_loop_core])
    tag_surf_core = gmsh.model.geo.addPlaneSurface([tag_loop_core])

    gmsh.model.geo.addPhysicalGroup(2, [tag_surf_air], name='air')
    gmsh.model.geo.addPhysicalGroup(2, [tag_surf_core], name='core')
    gmsh.model.geo.addPhysicalGroup(2, [tag_surf_cladding], name='cladding')
    gmsh.model.geo.addPhysicalGroup(
        1, [tag_arc_box0, tag_arc_box1, tag_arc_box2, tag_arc_box3], name='bound')
    gmsh.model.geo.addPhysicalGroup(
        1, [tag_arc_core0, tag_arc_core1, tag_arc_core2, tag_arc_core3], name='interface_core')
    gmsh.model.geo.addPhysicalGroup(
        1, [tag_arc_cladding0, tag_arc_cladding1, tag_arc_cladding2, tag_arc_cladding3], name='interface_cladding')

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    # gmsh.fltk.run()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write('skfem_scatterer.msh')
    gmsh.finalize()


mesh()

import numpy as np
import skfem
from skfem_helimi import Helmholtz, get_curvature
from skfem.visuals.matplotlib import draw, show, plot
import matplotlib.pyplot as mplt
from timeit import default_timer as timer
import os


# wavelength (in layout units) and normalized wave number
lambda_laser = 20
k0 = 2 * np.pi / lambda_laser

# angle (direction of travel) of incident wave; in radiant [0, 2*pi]
theta_laser = 0

# simulation settings (empty domain, polarization)
empty = False
pol = 'tm'

plotpath = './plots'
if not os.path.exists(plotpath):
    os.makedirs(plotpath)

print('Loading mesh')
t1 = timer()
mesh = skfem.Mesh.load('skfem_scatterer.msh')
t2 = timer()
print(f'Loading took {t2 - t1:.3f} s\n')

print('Init FEM')
element = skfem.ElementTriP3()
fem = Helmholtz(mesh, element)

print('\nAssembly')
t1 = timer()

# material parameters
if empty:
    eps_air = 1
    mu_air = 1
    eps_core = 1
    mu_core = 1
    eps_cladding = 1
    mu_cladding = 1
    plotname = 'skfem_scatterer_empty'
else:
    eps_air = 1.0
    mu_air = 1.0
    eps_core = 1.4475 ** 2
    mu_core = 1.0
    eps_cladding = 1.444 ** 2
    mu_cladding = 1.0
    plotname = 'skfem_scatterer_fiber'

# simulation parameters
if pol.lower() == 'tm':
    # for TM polarization
    alpha_air = 1 / mu_air
    alpha_core = 1 / mu_core
    alpha_cladding = 1 / mu_cladding
    beta_air = -1 * k0 ** 2 * eps_air
    beta_core = -1 * k0 ** 2 * eps_core
    beta_cladding = -1 * k0 ** 2 * eps_cladding
    field = 'Ez'
elif pol.lower() == 'te':
    # for TE polarization
    alpha_air = 1 / eps_air
    alpha_core = 1 / eps_core
    alpha_cladding = 1 / eps_cladding
    beta_air = -1 * k0 ** 2 * mu_air
    beta_core = -1 * k0 ** 2 * mu_core
    beta_cladding = -1 * k0 ** 2 * mu_cladding
    field = 'Hz'
else:
    raise ValueError(f'Invalid polarization pol=`{pol}`.')

# assemble all three subdomains
fem.assemble_subdomains(alpha={'air': alpha_air,
                               'core': alpha_core,
                               'cladding': alpha_cladding},
                        beta={'air': beta_air,
                              'core': beta_core,
                              'cladding': beta_cladding})

# assemble boundary conditions

# get boundary locations (coordinates) and curvature
x, y = fem.basis.doflocs[:, fem.basis.get_dofs()]
r = np.sqrt(x ** 2 + y ** 2)
kappa = get_curvature(x, y, wrapped=True)

# calculate incident field at boundary
kr = k0 * (x * np.cos(theta_laser) + y * np.sin(theta_laser))

phi0 = 1.0 * np.exp(-1j * kr)
dphi0_dn = -1j * kr / r * phi0
d2phi0_ds2 = (-1j * k0 / r * (-y * np.cos(theta_laser) +
              x * np.sin(theta_laser))) ** 2 * phi0

# first order absorbing boundary condition
g1 = 1j * k0 + kappa / 2
g2 = 0

# second order absorbing boundary condition
# g1 = 1j * k0 + kappa / 2 - 1j * kappa ** 2 / (8 * (1j * kappa - k0))
# g2 = -1j / (2 * (1j * kappa - k0))

q = alpha_air * (dphi0_dn + g1 * phi0 + g2 * d2phi0_ds2)
fem.assemble_boundaries_3rd(gamma={'bound': alpha_air * g1},
                            gamma2={'bound': alpha_air * g2},
                            q={'bound': q})
t2 = timer()
print(f'Assembly took {t2 - t1:.3f} s\n')

print(f'Solving for {2 * fem.basis.N} unknowns')
t1 = timer()
fem.solve(direct=True, cuda=False)
t2 = timer()
print(f'Solving took {t2 - t1:.3f} s\n')

ax = draw(fem.mesh, boundaries_only=True)
plot(fem.basis, np.abs(fem.phi), ax=ax, colorbar=True)
mplt.savefig('skfem_scatterer_solution.png')

print('near2far()')
t1 = timer()
x_farfield = 10000
y_farfield = np.linspace(-30000, 30000, 3001)
phi_farfield = np.zeros_like(y_farfield, dtype=complex)
for i in range(len(y_farfield)):
    phi_farfield[i] = fem.near2far(
        r=(x_farfield, y_farfield[i]), k=k0, field=fem.phi, boundaries=['bound'])
t2 = timer()
print(f'near2far() took {t2 - t1:.3f} s\n')

fig, ax = mplt.subplots(1, 2, figsize=(
    13, 7), gridspec_kw={'width_ratios': [3, 1]})
plot(fem.basis, fem.phi.real, shading='gouraud', colorbar=True, ax=ax[0])
draw(mesh, boundaries_only=True, ax=ax[0])
ax[0].set_aspect(1)
ax[0].set_title(f'Real part of {field} field')
ax[1].plot(np.real(phi_farfield), y_farfield, label='Real')
ax[1].plot(np.imag(phi_farfield), y_farfield, label='Imaginary')
ax[1].plot(np.abs(phi_farfield), y_farfield, label='Magnitude')
ax[1].legend()
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_ylabel('y farfield')
ax[1].set_title(f'Farfield at $x={x_farfield}$')
mplt.tight_layout()
# mplt.show()
mplt.savefig(f'{plotname}_{field}.png', dpi=300)
mplt.close()

fig, ax = mplt.subplots(1, 2, figsize=(
    13, 7), gridspec_kw={'width_ratios': [3, 1]})
plot(fem.basis, np.abs(fem.phi) ** 2,
     shading='gouraud', colorbar=True, ax=ax[0])
draw(mesh, boundaries_only=True, ax=ax[0])
ax[0].set_aspect(1)
ax[0].set_title(f'Intensity |{field}|²')
ax[1].plot(np.abs(phi_farfield) ** 2, y_farfield)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].set_ylabel('y farfield')
ax[1].set_title(f'Farfield intensity at $x={x_farfield}$')
mplt.tight_layout()
# mplt.show()
mplt.savefig(f'{plotname}_{field}_intensity.png', dpi=300)
mplt.close()
