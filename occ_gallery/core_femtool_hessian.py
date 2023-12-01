import numpy as np
import matplotlib.pyplot as plt


def hessian(x):
    """
    Calculate the hessian matrix with finite differences
    Parameters:
       - x : ndarray
    Returns:
       an array of shape (x.dim, x.ndim) + x.shape
       where the array[i, j, ...] corresponds to the second derivative x_ij
    """
    x_grad = np.gradient(x)
    hessian = np.empty((x.ndim, x.ndim) + x.shape, dtype=x.dtype)
    for k, grad_k in enumerate(x_grad):
        # iterate over dimensions
        # apply gradient again to every component of the first derivative.
        tmp_grad = np.gradient(grad_k)
        for l, grad_kl in enumerate(tmp_grad):
            hessian[k, l, :, :] = grad_kl
    return hessian


x = np.random.randn(100, 100, 100)
xh = hessian(x)
print(x.shape)
print(xh.shape)

from OCC.Core.math import math_Vector, math_Matrix
from OCC.Core.FEmTool import FEmTool_SparseMatrix, FEmTool_LinearTension
from OCC.Core.GeomAbs import GeomAbs_Shape, GeomAbs_C0, GeomAbs_C1

n1 = 11
n2 = 12
x = np.random.randn(n1)
b = np.random.randn(n1)
m = np.random.randn(n1, n2)
vec_x = math_Vector(1, n1)
vec_b = math_Vector(1, n1)
for i in range(vec_x.Lower(), vec_x.Upper()):
    vec_x.SetValue(i, x[i])
    vec_b.SetValue(i, b[i])
mat = math_Matrix(1, n1, 1, n2)
for (i, j), v in np.ndenumerate(m):
    mat.SetValue(i + 1, j + 1, v)

# a = FEmTool_LinearTension(3, GeomAbs_C1)
# print(a)
# print(a.Gradient(2, vec_b))
# print(a.Hessian(3, 3, mat))
# print(a.Value())
# mat = FEmTool_SparseMatrix(True)
# mat.Solve(vec_b, vec_x)
