import sys
import gmsh


def mesh(plane: str = 'h'):
    # WR6 standard gain horn (Pasternack PEWAN1028)
    # https://www.pasternack.com/images/ProductPDF/PEWAN1028.pdf

    if plane.lower() == 'e':
        h_waveg = 0.83
        h_horn = 13
    elif plane.lower() == 'h':
        h_waveg = 1.65
        h_horn = 17.5
    else:
        raise ValueError(f'Invalid parameter {plane}.')

    unit = 1e-3
    r_freespace = 20
    l_waveg = 4.11
    l_horn = 40.85

    wavelen = 3e8 / 200e9 / unit
    meshsize = wavelen / 8

    gmsh.initialize()
    gmsh.model.add('Waveguide horn')

    tag_pt_feed_ymin = gmsh.model.geo.addPoint(-1.0 * l_waveg - l_horn,
                                               -0.5 * h_waveg,
                                               0, meshSize=meshsize)
    tag_pt_feed_ymax = gmsh.model.geo.addPoint(-1.0 * l_waveg - l_horn,
                                               0.5 * h_waveg,
                                               0, meshSize=meshsize)
    tag_pt_feed_y0 = gmsh.model.geo.addPoint(-1 * l_waveg - l_horn,
                                             0,
                                             0, meshSize=meshsize)
    tag_pt_hornfeed_ymin = gmsh.model.geo.addPoint(-1.0 * l_horn,
                                                   -0.5 * h_waveg,
                                                   0, meshSize=meshsize)
    tag_pt_hornfeed_ymax = gmsh.model.geo.addPoint(-1.0 * l_horn,
                                                   0.5 * h_waveg,
                                                   0, meshSize=meshsize)
    tag_pt_hornfeed_y0 = gmsh.model.geo.addPoint(-1 * l_horn,
                                                 0,
                                                 0, meshSize=meshsize)
    tag_pt_horn_ymin = gmsh.model.geo.addPoint(0,
                                               -0.5 * h_horn,
                                               0, meshSize=meshsize)
    tag_pt_horn_ymax = gmsh.model.geo.addPoint(0, 0.5 * h_horn,
                                               0,
                                               meshSize=meshsize)
    tag_pt_horn_y0 = gmsh.model.geo.addPoint(0, 0, 0, meshSize=meshsize)
    tag_pt_arc_ymin = gmsh.model.geo.addPoint(0,
                                              -1 * r_freespace,
                                              0, meshSize=meshsize)
    tag_pt_arc_ymax = gmsh.model.geo.addPoint(0,
                                              r_freespace,
                                              0, meshSize=meshsize)
    tag_pt_arc_y0 = gmsh.model.geo.addPoint(r_freespace,
                                            0,
                                            0, meshSize=meshsize)

    tag_line_feed = gmsh.model.geo.addLine(tag_pt_feed_ymin, tag_pt_feed_ymax)
    tag_line_waveg_ymax = gmsh.model.geo.addLine(tag_pt_feed_ymax,
                                                 tag_pt_hornfeed_ymax)
    tag_line_horn_ymax = gmsh.model.geo.addLine(tag_pt_hornfeed_ymax,
                                                tag_pt_horn_ymax)
    tag_line_freespace_ymax = gmsh.model.geo.addLine(tag_pt_horn_ymax,
                                                     tag_pt_arc_ymax)
    tag_arc_freespace_ymax = gmsh.model.geo.addCircleArc(tag_pt_arc_ymax,
                                                         tag_pt_horn_y0,
                                                         tag_pt_arc_y0)
    tag_arc_freespace_ymin = gmsh.model.geo.addCircleArc(tag_pt_arc_y0,
                                                         tag_pt_horn_y0,
                                                         tag_pt_arc_ymin)
    tag_line_freespace_ymin = gmsh.model.geo.addLine(tag_pt_arc_ymin,
                                                     tag_pt_horn_ymin)
    tag_line_horn_ymin = gmsh.model.geo.addLine(tag_pt_horn_ymin,
                                                tag_pt_hornfeed_ymin)
    tag_line_waveg_ymin = gmsh.model.geo.addLine(tag_pt_hornfeed_ymin,
                                                 tag_pt_feed_ymin)

    tag_loop = gmsh.model.geo.addCurveLoop([tag_line_feed,
                                            tag_line_waveg_ymax,
                                            tag_line_horn_ymax,
                                            tag_line_freespace_ymax,
                                            tag_arc_freespace_ymax,
                                            tag_arc_freespace_ymin,
                                            tag_line_freespace_ymin,
                                            tag_line_horn_ymin,
                                            tag_line_waveg_ymin])

    tag_surf = gmsh.model.geo.addPlaneSurface([tag_loop])

    gmsh.model.geo.addPhysicalGroup(2, [tag_surf], name='air')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line_feed], name='bound_feed')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line_freespace_ymax,
                                        tag_arc_freespace_ymax,
                                        tag_arc_freespace_ymin,
                                        tag_line_freespace_ymin], name='bound_freespace')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line_waveg_ymax,
                                        tag_line_horn_ymax], name='bound_ymax')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line_waveg_ymin,
                                        tag_line_horn_ymin], name='bound_ymin')

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    # gmsh.fltk.run()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(f'skfem_horn_{plane}-plane.msh')
    gmsh.finalize()


# if __name__ == '__main__':
#    if len(sys.argv) > 1:
#        plane = sys.argv[1]
#    else:
#        plane = 'e'
#    mesh(plane)

import numpy as np
import skfem
from skfem_helimi import Helmholtz
from skfem.visuals.matplotlib import plot
from scipy.constants import epsilon_0, mu_0
import matplotlib.pyplot as mplt
from timeit import default_timer as timer
import os

# parameters
unit = 1e-3
plane = 'h'
plane = 'e'
f = 140e9
n = 1
eps_r = 1.0
mu_r = 1.0
k0 = 2 * np.pi * f * np.sqrt(epsilon_0 * mu_0) * unit
z0 = np.sqrt(mu_0 / epsilon_0) * unit

plotpath = './plots'
if not os.path.exists(plotpath):
    os.makedirs(plotpath)

print('Meshing...')
t1 = timer()
mesh(plane)
mesh = skfem.Mesh.load(f'skfem_horn_{plane}-plane.msh')
t2 = timer()
print(f'Meshing took {t2 - t1:.3f} s\n')

print('Init FEM...')
element = skfem.ElementTriP2()
fem = Helmholtz(mesh, element)

print('\nAssembly...')
t1 = timer()
if plane == 'e':
    # TE; phi=Hz
    alpha = 1 / eps_r
    beta = -1 * k0 ** 2 * mu_r
    coeff_complementary = -1 * z0 / k0 * alpha
else:
    # TM; phi=Ez
    alpha = 1 / mu_r
    beta = -1 * k0 ** 2 * eps_r
    coeff_complementary = 1 / z0 / k0 * alpha
    fem.assemble_boundaries_dirichlet(value={'bound_ymin': 0, 
                                             'bound_ymax': 0})

fem.assemble_subdomains(alpha={'air': alpha}, beta={'air': beta})
fem.assemble_boundaries_3rd(gamma={'bound_feed': alpha * 1j * k0, 
                                   'bound_freespace': alpha * 1j * k0},
                            q={'bound_feed': alpha * 2j * k0, 
                               'bound_freespace': 0})
t2 = timer()
print(f'Assembly took {t2 - t1:.3f} s')

print('\nSolving...')
t1 = timer()
fem.solve(direct=True)
t2 = timer()
print(f'Solving took {t2 - t1:.3f} s\n')

print('near2far()...')
t1 = timer()
r_farfield = 100
theta_farfield = np.linspace(-0.5 * np.pi, 0.5 * np.pi, 181)
phi_farfield = np.zeros_like(theta_farfield, dtype=complex)
for i, theta_i in enumerate(theta_farfield):
    r_x = r_farfield * np.cos(theta_i)
    r_y = r_farfield * np.sin(theta_i)
    phi_farfield[i] = fem.near2far(
        r=(r_x, r_y), k=k0, field=fem.phi, boundaries=['bound_freespace'])
t2 = timer()
print(f'near2far() took {t2 - t1:.3f} s\n')

print('Post processing...')
phi_mag_farfield = np.abs(phi_farfield)
phi_db_farfield = 20 * np.log10(phi_mag_farfield / np.amax(phi_mag_farfield))

# dof locations (x, y) at x=xmin and at x=xmax
x_feed, y_feed = fem.basis.doflocs[:, fem.basis.get_dofs('bound_feed')]

# indices of center locations (y=0) at x=xmin and at x=xmax
i_feed_y0 = np.argmin(np.abs(y_feed - 0))

# get fields at (x=xmin, y=0) and at (x=xmax, y=0):
phi_feed = fem.phi[fem.basis.get_dofs('bound_feed')][i_feed_y0]

# calculate reflection and transmission coefficients
r = phi_feed / 1.0 - 1
print(f'r = {np.abs(r) ** 2} = {20 * np.log10(np.abs(r)):.1f} dB')

# complementary fields (in x-y plane);
phi_comp_x_re = -1 * coeff_complementary * \
    fem.basis.project(fem.basis.interpolate(fem.phi_im).grad[1])
# phi_comp_x_im = coeff_complementary * fem.basis.project(fem.basis.interpolate(fem.phi_re).grad[1])
# phi_comp_x = phi_comp_x_re + 1j * phi_comp_x_im

phi_comp_y_re = -1 * coeff_complementary * \
    fem.basis.project(fem.basis.interpolate(fem.phi_im).grad[0])
# phi_comp_y_im = coeff_complementary * fem.basis.project(fem.basis.interpolate(fem.phi_re).grad[0])
# phi_comp_y = phi_comp_y_re + 1j * phi_comp_y_im

fig, ax = mplt.subplots(2, 1, figsize=(8, 6))
fig.suptitle(f'Real parts of fields at f = {f * 1e-9} GHz')
# draw(mesh, ax=ax[0])
plot(fem.basis, fem.phi_re, colorbar=True, ax=ax[0])
ax[0].set_aspect('equal')
ax[0].set_title('Transverse field (Ez or Hz)')
# draw(mesh, ax=ax[1])
plot(fem.basis, phi_comp_x_re + phi_comp_y_re, colorbar=True, ax=ax[1])
ax[1].set_aspect('equal')
ax[1].set_title('Complementary field (Hx+Hy or Ex+Ey)')
fig.tight_layout()
mplt.savefig(f'skfem_horn_{plane}-plane_fields.png')
mplt.close()

mplt.figure()
mplt.polar(theta_farfield, phi_db_farfield)
mplt.title(f'Radiation pattern ({plane.upper()}-Plane, {f * 1e-9} GHz)')
mplt.tight_layout()
mplt.savefig(f'skfem_horn_{plane}-plane_pattern_polar.png')
mplt.close()

mplt.figure()
mplt.plot(np.rad2deg(theta_farfield), phi_db_farfield)
mplt.title(f'Radiation pattern ({plane.upper()}-Plane, {f * 1e-9} GHz)')
mplt.tight_layout()
mplt.savefig(f'skfem_horn_{plane}-plane_pattern_rect.png')
mplt.close()
