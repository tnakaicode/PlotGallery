import cvxpy as cp
import numpy as np
x = cp.Variable(2)
c = np.array([20.0, 60.0]).T
G = np.array([
    [5.0, 4.0],
    [2.0, 4.0],
    [2.0, 8.0],
    [-1.0, 0],
    [0, -1.0]])
h = [80.0, 40.0, 64.0, 0.0, 0.0]
obj = cp.Maximize(c.T * x)
cons = [G * x <= h]
P = cp.Problem(obj, cons)
P.solve(verbose=True)
print(x.value)
