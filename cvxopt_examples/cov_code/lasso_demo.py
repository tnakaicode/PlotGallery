import cvxpy as cp
import numpy as np
m, n, gam = 10, 5, 100.0
np.random.seed(2)
A = np.random.randn(m, n)
b = 100 * np.random.randn(m)
x, z = cp.Variable(n), cp.Variable(n)
obj = cp.Minimize(sum(cp.square(A * x - b))
                  + (gam * sum(z)))
cons = [z >= x,
        z >= -x]
P = cp.Problem(obj, cons)
P.solve(verbose=True)
print(x.value)
