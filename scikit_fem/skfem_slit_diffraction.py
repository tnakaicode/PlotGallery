import gmsh
import sys


def mesh(n_slits, w_slit, pitch):
    l_slit = 2.5
    r_box = 0.5 * pitch * (n_slits + 1)

    mesh_slit = 0.25
    mesh_box = 0.5

    if w_slit > pitch:
        raise ValueError('slit width > pitch')

    if 0.5 * n_slits * pitch > r_box:
        raise ValueError('box too small')

    gmsh.initialize()
    gmsh.model.add('Slit')

    tag_pt_center = gmsh.model.geo.addPoint(0, 0, 0)

    tag_pt_box_00 = gmsh.model.geo.addPoint(-0.5 *
                                            r_box, -1 * r_box, 0, meshSize=mesh_box)
    tag_pt_box_01 = gmsh.model.geo.addPoint(-0.5 *
                                            r_box, r_box, 0, meshSize=mesh_box)
    tag_pt_box_0c = gmsh.model.geo.addPoint(-0.5 *
                                            r_box, 0, 0, meshSize=mesh_box)
    tag_pt_box_c01 = gmsh.model.geo.addPoint(
        -0.5 * l_slit, r_box, 0, meshSize=mesh_box)
    tag_pt_box_c00 = gmsh.model.geo.addPoint(
        -0.5 * l_slit, -1 * r_box, 0, meshSize=mesh_box)
    tag_pt_box_c11 = gmsh.model.geo.addPoint(
        0.5 * l_slit, r_box, 0, meshSize=mesh_box)
    tag_pt_box_c10 = gmsh.model.geo.addPoint(
        0.5 * l_slit, -1 * r_box, 0, meshSize=mesh_box)
    tag_pt_box_1c = gmsh.model.geo.addPoint(r_box, 0, 0, meshSize=mesh_box)

    tag_arc_box_11 = gmsh.model.geo.addCircleArc(
        tag_pt_box_1c, tag_pt_center, tag_pt_box_c11)
    tag_arc_box_10 = gmsh.model.geo.addCircleArc(
        tag_pt_box_c10, tag_pt_center, tag_pt_box_1c)
    tag_line_box_c1 = gmsh.model.geo.addLine(tag_pt_box_c11, tag_pt_box_c01)
    tag_line_box_c0 = gmsh.model.geo.addLine(tag_pt_box_c00, tag_pt_box_c10)
    tag_line_box_01 = gmsh.model.geo.addLine(tag_pt_box_c01, tag_pt_box_01)
    tag_line_box_0c = gmsh.model.geo.addLine(tag_pt_box_01, tag_pt_box_00)
    tag_line_box_00 = gmsh.model.geo.addLine(tag_pt_box_00, tag_pt_box_c00)

    tag_loop_box = gmsh.model.geo.addCurveLoop([tag_arc_box_11, tag_line_box_c1, tag_line_box_01, tag_line_box_0c,
                                                tag_line_box_00, tag_line_box_c0, tag_arc_box_10])

    # slitted aperture (blind)
    height_blinds = pitch - w_slit
    height_aperture = n_slits * w_slit + (n_slits - 1) * height_blinds
    tag_pt_slit_01 = gmsh.model.geo.addPoint(
        -0.5 * l_slit, 0.5 * height_aperture, 0, meshSize=mesh_slit)
    tag_pt_slit_11 = gmsh.model.geo.addPoint(
        0.5 * l_slit, 0.5 * height_aperture, 0, meshSize=mesh_slit)
    tag_pt_slit_00 = gmsh.model.geo.addPoint(
        -0.5 * l_slit, -0.5 * height_aperture, 0, meshSize=mesh_slit)
    tag_pt_slit_10 = gmsh.model.geo.addPoint(
        0.5 * l_slit, -0.5 * height_aperture, 0, meshSize=mesh_slit)

    tag_line_blind_01 = gmsh.model.geo.addLine(tag_pt_box_c01, tag_pt_slit_01)
    tag_line_blind_h1 = gmsh.model.geo.addLine(tag_pt_slit_01, tag_pt_slit_11)
    tag_line_blind_11 = gmsh.model.geo.addLine(tag_pt_slit_11, tag_pt_box_c11)
    tag_loop_blind_1 = gmsh.model.geo.addCurveLoop(
        [tag_line_box_c1, tag_line_blind_01, tag_line_blind_h1, tag_line_blind_11])

    tag_line_blind_00 = gmsh.model.geo.addLine(tag_pt_box_c10, tag_pt_slit_10)
    tag_line_blind_h0 = gmsh.model.geo.addLine(tag_pt_slit_10, tag_pt_slit_00)
    tag_line_blind_10 = gmsh.model.geo.addLine(tag_pt_slit_00, tag_pt_box_c00)
    tag_loop_blind_0 = gmsh.model.geo.addCurveLoop(
        [tag_line_box_c0, tag_line_blind_00, tag_line_blind_h0, tag_line_blind_10])

    tags_loops_blind = [tag_loop_blind_0, tag_loop_blind_1]
    tags_lines_blind = [tag_line_blind_00, tag_line_blind_h0, tag_line_blind_10,
                        tag_line_blind_01, tag_line_blind_h1, tag_line_blind_11]

    for i in range(n_slits - 1):
        y_bot = -0.5 * height_aperture + i * pitch + w_slit
        y_top = y_bot + height_blinds
        tag_pt_01 = gmsh.model.geo.addPoint(-0.5 *
                                            l_slit, y_top, 0, meshSize=mesh_slit)
        tag_pt_00 = gmsh.model.geo.addPoint(-0.5 *
                                            l_slit, y_bot, 0, meshSize=mesh_slit)
        tag_pt_10 = gmsh.model.geo.addPoint(
            0.5 * l_slit, y_bot, 0, meshSize=mesh_slit)
        tag_pt_11 = gmsh.model.geo.addPoint(
            0.5 * l_slit, y_top, 0, meshSize=mesh_slit)
        tag_line_0c = gmsh.model.geo.addLine(tag_pt_01, tag_pt_00)
        tag_line_c0 = gmsh.model.geo.addLine(tag_pt_00, tag_pt_10)
        tag_line_1c = gmsh.model.geo.addLine(tag_pt_10, tag_pt_11)
        tag_line_c1 = gmsh.model.geo.addLine(tag_pt_11, tag_pt_01)
        tag_loop = gmsh.model.geo.addCurveLoop(
            [tag_line_0c, tag_line_c0, tag_line_1c, tag_line_c1])
        tags_loops_blind.append(tag_loop)
        tags_lines_blind.append(tag_line_0c)
        tags_lines_blind.append(tag_line_c0)
        tags_lines_blind.append(tag_line_1c)
        tags_lines_blind.append(tag_line_c1)

    tag_surf_air = gmsh.model.geo.addPlaneSurface(
        [tag_loop_box, *tags_loops_blind])

    gmsh.model.geo.addPhysicalGroup(2, [tag_surf_air], name='air')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line_box_0c], name='bounds_left')
    gmsh.model.geo.addPhysicalGroup(
        1, [tag_arc_box_10, tag_arc_box_11], name='bounds_right')
    gmsh.model.geo.addPhysicalGroup(
        1, tags_lines_blind, name='bounds_aperture')

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    # gmsh.fltk.run()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write('skfem_slit.msh')
    gmsh.finalize()


n_slits = 3
w_slit = 10
pitch = 20
mesh(n_slits, w_slit, pitch)

import numpy as np
import skfem
from skfem_helimi import Helmholtz, get_curvature
from skfem.visuals.matplotlib import draw, show, plot
import matplotlib.pyplot as mplt
from timeit import default_timer as timer

# wavelength (in layout units) and normalized wave number
wavelength = 2
k0 = 2 * np.pi / wavelength

# slit parameters
n_slits = 3
w_slit = 10
pitch = 20

# angle (direction of travel) of incident wave; in radiant [0, 2*pi]
theta_laser = 0

# material parameters
eps_air = 1.0
mu_air = 1.0

print('Loading mesh')
t1 = timer()
mesh = skfem.Mesh.load('skfem_slit.msh')
t2 = timer()
print(f'Loading took {t2 - t1:.3f} s\n')

print('Init FEM')
element = skfem.ElementTriP2()
fem = Helmholtz(mesh, element)

print('\nAssembly')
t1 = timer()

# calculate incident field at left-side boundaries
x, y = fem.basis.doflocs[:, fem.basis.get_dofs('bounds_left')]
r = np.sqrt(x ** 2 + y ** 2)
kr = k0 * (x * np.cos(theta_laser) + y * np.sin(theta_laser))
phi0 = 1.0 * np.exp(-1j * kr)
dphi0_dn = -1j * kr / r * phi0

# simulation parameters for TM polarization
alpha_air = 1 / mu_air
beta_air = -1 * k0 ** 2 * eps_air
fem.assemble_subdomains(alpha={'air': alpha_air}, beta={'air': beta_air})
fem.assemble_boundaries_dirichlet(value={'bounds_aperture': 0})

# first order absorber
g_left = 1j * k0
x_right, y_right = fem.basis.doflocs[:, fem.basis.get_dofs('bounds_right')]
g_right = 1j * k0 + get_curvature(x_right, y_right) / 2

fem.assemble_boundaries_3rd(gamma={'bounds_left': alpha_air * g_left,
                                   'bounds_right': alpha_air * g_right},
                            q={'bounds_left': alpha_air * (dphi0_dn + g_left * phi0),
                               'bounds_right': 0})
t2 = timer()
print(f'Assembly took {t2 - t1:.3f} s\n')

print(f'Solving for {2 * fem.basis.N} unknowns')
t1 = timer()
fem.solve(direct=True, cuda=False)
t2 = timer()
print(f'Solving took {t2 - t1:.3f} s\n')

from skfem.visuals.matplotlib import plot, savefig, show, draw
#M, X = fem.basis.refinterp(np.abs(fem.phi), 4)
ax = draw(fem.mesh, boundaries_only=True)
plot(fem.basis, np.abs(fem.phi), ax=ax, colorbar=True)
savefig('skfem_slit_solution.png')

print('near2far()')
t1 = timer()
x_farfield = 1000
y_farfield = np.linspace(-1000, 1000, 401)
phi_farfield = np.zeros_like(y_farfield, dtype=complex)
for i in range(len(y_farfield)):
    phi_farfield[i] = fem.near2far(
        r=(x_farfield, y_farfield[i]), k=k0, field=fem.phi, boundaries=['bounds_right'])
t2 = timer()
print(f'near2far() took {t2 - t1:.3f} s\n')

# theoretical intensity distribution in diffraction gratings
# https://sites.ualberta.ca/~pogosyan/teaching/PHYS_130/FALL_2010/lectures/lect36/lecture36.html
sin_theta = y_farfield / x_farfield
slits = np.array(range(n_slits))
delta_theta = (slits[:, None] - 0.5 * (n_slits - 1)) * k0 * pitch * sin_theta
r = np.sqrt(x_farfield ** 2 + y_farfield ** 2)
phi_farfield_ideal = np.amax(np.abs(phi_farfield)) * np.sinc(k0 / 2 / np.pi *
                                                             w_slit * sin_theta) * np.mean(np.exp(-1j * (k0 * r + delta_theta)), axis=0)

fig, ax = mplt.subplots(1, 2, figsize=(
    13, 7), gridspec_kw={'width_ratios': [3, 1]})
#plot(fem.basis, fem.phi.real, shading='gouraud', colorbar=True, ax=ax[0])
ax[0].set_aspect(1)
ax[1].plot(np.abs(phi_farfield), y_farfield, label='FEM')
ax[1].plot(np.abs(phi_farfield_ideal), y_farfield, label='Theory')
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position('right')
ax[1].yaxis.tick_right()
ax[1].legend()
mplt.tight_layout()
# mplt.show()
mplt.savefig(f'skfem_slit_{n_slits}_{w_slit}_{pitch}.png', dpi=600)
mplt.close()
