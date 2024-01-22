r"""Adaptive Poisson equation.

This example solves `ex01.py` adaptively in an L-shaped domain.
Using linear elements, the error indicators read

.. math::
   \eta_K^2 = h_K^2 \|f\|_{0,K}^2
for each element :math:`K`, and

.. math::
   \eta_E^2 = h_E \| [[\nabla u_h \cdot n ]] \|_{0,E}^2
for each edge :math:`E`.

"""
import skfem
from skfem import MeshTri1, ElementTriP1, LinearForm, Basis, Functional, InteriorFacetBasis, solve, condense, adaptive_theta
from skfem.models.poisson import laplace
from skfem.helpers import grad
import numpy as np
import gmsh
from os.path import splitext
from sys import argv

def make_mesh():
    meshsize = 0.1

    gmsh.initialize()
    gmsh.model.add('box')

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

    #gmsh.model.geo.addPhysicalGroup(2, [tag_surf], name='air')
    #gmsh.model.geo.addPhysicalGroup(1, [tag_line0, tag_line1, tag_line3, tag_line4], name='plastic')
    #gmsh.model.geo.addPhysicalGroup(1, [tag_line5], name='bound_ymax')
    #gmsh.model.geo.addPhysicalGroup(1, [tag_line2], name='bound_ymin')
    #gmsh.model.geo.addPhysicalGroup(1, [tag_line3], name='bound_xmax')
    #gmsh.model.geo.addPhysicalGroup(1, [tag_line5], name='bound_xmin')

    gmsh.model.geo.synchronize()
    gmsh.model.mesh.generate(2)
    #gmsh.fltk.run()
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(splitext(argv[0])[0] + '.msh')
    gmsh.finalize()

make_mesh()
m = skfem.Mesh.load(splitext(argv[0])[0] + '.msh')
#m = MeshTri1.init_lshaped().refined(2)
e = ElementTriP1()


def load_func(x, y):
    return 1.


@LinearForm
def load(v, w):
    x, y = w.x
    return load_func(x, y) * v


def eval_estimator(m, u):
    # interior residual
    basis = Basis(m, e)

    @Functional
    def interior_residual(w):
        h = w.h
        x, y = w.x
        return h ** 2 * load_func(x, y) ** 2

    eta_K = interior_residual.elemental(basis, w=basis.interpolate(u))

    # facet jump
    fbasis = [InteriorFacetBasis(m, e, side=i) for i in [0, 1]]
    w = {'u' + str(i + 1): fbasis[i].interpolate(u) for i in [0, 1]}

    @Functional
    def edge_jump(w):
        h = w.h
        n = w.n
        dw1 = grad(w['u1'])
        dw2 = grad(w['u2'])
        return h * ((dw1[0] - dw2[0]) * n[0] +
                    (dw1[1] - dw2[1]) * n[1]) ** 2

    eta_E = edge_jump.elemental(fbasis[0], **w)

    tmp = np.zeros(m.facets.shape[1])
    np.add.at(tmp, fbasis[0].find, eta_E)
    eta_E = np.sum(.5 * tmp[m.t2f], axis=0)

    return eta_K + eta_E

# if __name__ == "__main__":
#    from skfem.visuals.matplotlib import draw
#    draw(m)


for itr in reversed(range(1)):
    basis = Basis(m, e)

    K = laplace.assemble(basis)
    f = load.assemble(basis)

    I = m.interior_nodes()
    u = solve(*condense(K, f, I=I))

    if itr > 0:
        m = m.refined(adaptive_theta(eval_estimator(m, u))).smoothed()


def visualize():
    from skfem.visuals.matplotlib import draw, plot
    ax = draw(m)
    return plot(m, u, ax=ax, shading='gouraud', colorbar=True)


if __name__ == "__main__":
    from skfem.visuals.matplotlib import draw, plot, savefig, show
    #ax = draw(m)
    plot(m, u, shading='gouraud', colorbar=True)
    savefig(splitext(argv[0])[0] + '_solution.png')
    show()
