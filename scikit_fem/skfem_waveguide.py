import skfem
from skfem_helimi import Helmholtz, get_curvature
import numpy as np
import gmsh


def make_mesh(plane: str = 'h'):
    meshsize = 1.0

    gmsh.initialize()
    gmsh.model.add('Waveguide')

    tag_pt0 = gmsh.model.geo.addPoint(0, -5, 0, meshSize=meshsize)
    tag_pt1 = gmsh.model.geo.addPoint(50, -5, 0, meshSize=meshsize)
    tag_pt2 = gmsh.model.geo.addPoint(50, -25, 0, meshSize=meshsize)
    tag_pt3 = gmsh.model.geo.addPoint(60, -25, 0, meshSize=meshsize)
    tag_pt4 = gmsh.model.geo.addPoint(60, 5, 0, meshSize=meshsize)
    tag_pt5 = gmsh.model.geo.addPoint(0, 5, 0, meshSize=meshsize)

    tag_line0 = gmsh.model.geo.addLine(tag_pt0, tag_pt1)
    tag_line1 = gmsh.model.geo.addLine(tag_pt1, tag_pt2)
    tag_line2 = gmsh.model.geo.addLine(tag_pt2, tag_pt3)
    tag_line3 = gmsh.model.geo.addLine(tag_pt3, tag_pt4)
    tag_line4 = gmsh.model.geo.addLine(tag_pt4, tag_pt5)
    tag_line5 = gmsh.model.geo.addLine(tag_pt5, tag_pt0)

    tag_loop = gmsh.model.geo.addCurveLoop([tag_line0, tag_line1, tag_line2, 
                                            tag_line3, tag_line4, tag_line5])
    tag_surf = gmsh.model.geo.addPlaneSurface([tag_loop])

    gmsh.model.geo.addPhysicalGroup(2, [tag_surf], name='air')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line0, tag_line1, tag_line3, tag_line4], name='plastic')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line5], name='bound_ymax')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line2], name='bound_ymin')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line3], name='bound_xmax')
    gmsh.model.geo.addPhysicalGroup(1, [tag_line5], name='bound_xmin')

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.fltk.run()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(f'skfem_waveguide.msh')
    gmsh.finalize()


make_mesh()
# x_pts = np.linspace(0, 100, 101)
# y_pts = np.linspace(-5, 5, 21)
# mesh = skfem.MeshTri.init_tensor(x_pts, y_pts)
# mesh = mesh.with_subdomains({'air': lambda x: x[0] < 50,
#                             'plastic': lambda x: x[0] >= 50})
# mesh = mesh.with_boundaries({'bound_xmin': lambda x: np.isclose(x[0], x_pts[0]),
#                             'bound_xmax': lambda x: np.isclose(x[0], x_pts[-1]),
#                             'bound_ymin': lambda x: np.isclose(x[1], y_pts[0]),
#                             'bound_ymax': lambda x: np.isclose(x[1], y_pts[-1])})

mesh = skfem.Mesh.load(f'skfem_waveguide.msh')
element = skfem.ElementTriP2()
fem = Helmholtz(mesh, element)

unit = 1e-3
k0 = 0.5
eps_air = 1
mu_air = 1
eps_plastic = 2 - 0.1j
mu_plastic = 1

print('\nAssembly...')
fem.assemble_subdomains(alpha={'air': 1 / mu_air,
                               'plastic': 1 / mu_plastic},
                        beta={'air': -1 * k0 ** 2 * eps_air,
                              'plastic': -1 * k0 ** 2 * eps_plastic},
                        f={'air': 0,
                           'plastic': 0})

fem.assemble_boundaries_dirichlet(value={'bound_ymin': 0,
                                         'bound_ymax': 0})

fem.assemble_boundaries_3rd(gamma={'bound_xmin': 1 / mu_air * 1j * k0,
                                   'bound_xmax': 1 / mu_plastic * 1j * k0},
                            q={'bound_xmin': 1 / mu_air * 2j * k0,
                               'bound_xmax': 0})
print('\nSolving...')
from timeit import default_timer as timer
t1 = timer()
fem.solve()
t2 = timer()
print(f'Solving took {t2 - t1:.3f} s\n')

from skfem.visuals.matplotlib import plot
import matplotlib.pyplot as mplt

fig, ax = mplt.subplots(2, 1, figsize=(10, 4))
plot(fem.basis, fem.phi_re, ax=ax[0])
plot(fem.basis, fem.phi_im, ax=ax[1])
ax[0].set_aspect(1)
ax[1].set_aspect(1)
ax[0].set_title('Real Part')
ax[1].set_title('Imaginary Part')
mplt.tight_layout()
mplt.savefig('skfem_waveguide.png')
mplt.close()
