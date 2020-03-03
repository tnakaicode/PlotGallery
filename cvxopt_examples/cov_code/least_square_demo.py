import cvxpy as cp
import numpy as np
r = 20
np.random.seed(1)
A = np.hstack((np.random.randn(r, 1), np.ones([r, 1])))
c = np.array([A[:, 0]]).T
b = (10.0 * np.random.randn() * c) + \
    + (0.5 * np.random.randn(r, 1))
b = b.T.tolist()
x = cp.Variable(2)
obj = cp.Minimize(sum(cp.square(A * x - b)))
P = cp.Problem(obj)
P.solve(verbose=True)
print(x.value)
