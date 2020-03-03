import cvxpy as cp
import numpy as np
m, n, g = 10, 5, 0.1
np.random.seed(1)
A, b = np.random.randn(m, n), 10 * np.random.randn(m)
x = cp.Variable(n)
z = cp.Variable()
w = cp.Variable(n)
obj = cp.Minimize(z + (g * sum(w)))
cons = [z >= cp.norm(A * x - b),
        w >= cp.abs(x)]
P = cp.Problem(obj, cons)
P.solve(verbose=True)
print(P.value)
print(x.value)
