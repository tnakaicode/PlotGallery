# https://scikit-fem.readthedocs.io/en/latest/listofexamples.html

from skfem import MeshTri1, MeshQuad, Basis, BilinearForm, LinearForm, ElementTriP1, enforce, solve
from skfem.visuals.matplotlib import plot, draw
from skfem.helpers import dot, grad

# create the mesh
mesh = MeshTri1().refined(5)
mesh = MeshTri1().init_circle(4)
# or, with your own points and elements:
# mesh = MeshTri(points, elements)

basis = Basis(mesh, ElementTriP1())


@BilinearForm
def laplace(u, v, _):
    return dot(grad(u), grad(v))


@LinearForm
def rhs(v, _):
    return 1. * v


A = laplace.assemble(basis)
b = rhs.assemble(basis)
print(A, b)

# Dirichlet boundary conditions
A, b = enforce(A, b, D=mesh.boundary_nodes())

# solve the linear system
x = solve(A, b)
M, X = basis.refinterp(x, 4)

ax = draw(M, boundaries_only=True)

# plot using matplotlib
plot(M, X, shading='gouraud', ax=ax, colorbar=True)
mesh.plot(x, shading='gouraud', colorbar=True).show()
# or, save to external file:
mesh.save('skfem_ex01.vtk', point_data={'solution': x})
mesh.save('skfem_ex01.xdmf', point_data={'solution': x})

# Poisson equation
#  Example 1: Poisson equation with unit load
#  Example 7: Discontinuous Galerkin method
#  Example 12: Postprocessing
#  Example 13: Laplace with mixed boundary conditions
#  Example 14: Laplace with inhomogeneous boundary conditions
#  Example 15: One-dimensional Poisson equation
#  Example 9: Three-dimensional Poisson equation
#  Example 22: Adaptive Poisson equation
#  Example 37: Mixed Poisson equation
#  Example 38: Point source
#  Example 40: Hybridizable discontinuous Galerkin method
#  Example 41: Mixed meshes
# Solid mechanics
#  Example 2: Kirchhoff plate bending problem
#  Example 3: Linear elastic eigenvalue problem
#  Example 4: Linearized contact problem
#  Example 8: Argyris basis functions
#  Example 11: Three-dimensional linear elasticity
#  Example 21: Structural vibration
#  Example 34: Euler-Bernoulli beam
#  Example 36: Nearly incompressible hyperelasticity
#  Example 43: Hyperelasticity
# Fluid mechanics
#  Example 18: Stokes equations
#  Example 20: Creeping flow via stream-function
#  Example 24: Stokes flow with inhomogeneous boundary conditions
#  Example 29: Linear hydrodynamic stability
#  Example 30: Krylov-Uzawa method for the Stokes equation
#  Example 32: Block diagonally preconditioned Stokes solver
#  Example 42: Periodic meshes
# Heat transfer
#  Example 17: Insulated wire
#  Example 19: Heat equation
#  Example 25: Forced convection
#  Example 26: Restricting problem to a subdomain
#  Example 28: Conjugate heat transfer
#  Example 39: One-dimensional heat equation
# Miscellaneous
#  Example 10: Nonlinear minimal surface problem
#  Example 16: Legendre’s equation
#  Example 31: Curved elements
#  Example 33: H(curl) conforming model problem
#  Example 35: Characteristic impedance and velocity factor
#  Example 44: Wave equation
# 