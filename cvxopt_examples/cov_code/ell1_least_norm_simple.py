import cvxpy as cp
import numpy as np
m, n, g = 10, 5, 0.1
np.random.seed(1)
A, b = np.random.randn(m, n), 10 * np.random.randn(m)
x = cp.Variable(n)
obj = cp.Minimize(cp.norm(A * x - b)
                  + (g * sum(cp.abs(x))))
P = cp.Problem(obj)
P.solve(verbose=True)
print(x.value)
