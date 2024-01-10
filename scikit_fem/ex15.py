"""One-dimensional Poisson."""

import numpy as np
from skfem import *
from skfem.models.poisson import laplace, unit_load

m = MeshLine(np.linspace(0, 1, 10))

e = ElementLineP1()
basis = Basis(m, e)

A = asm(laplace, basis)
b = asm(unit_load, basis)

x = solve(*condense(A, b, D=basis.get_dofs()))

if __name__ == "__main__":
    from os.path import splitext
    from sys import argv
    from skfem.visuals.matplotlib import plot, savefig, show, draw
    
    plot(m, x, shading='gouraud', colorbar=True)
    savefig(splitext(argv[0])[0] + '_solution.png')
    show()
