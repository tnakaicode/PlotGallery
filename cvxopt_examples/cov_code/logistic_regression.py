import cvxpy as cp
import numpy as np
S = np.array([
    [-2.05, -1.20, -1.05, -0.82, -0.27,
     -0.28, 0.03, 0.50, 0.82, 1.12],
    [-0.35, 2.90, -0.46, -1.57, 0.70,
     1.09, -1.33, 0.28, 1.37, 0.35]])
t = [1, -1, 1, 1, -1, -1, 1, -1, -1, 1]
d = S.shape[0]
w, v = cp.Variable(d), cp.Variable()
z = -cp.diag(t) * (S.T * w + v)
obj = cp.Minimize(sum(cp.logistic(z)))
P = cp.Problem(obj)
P.solve(verbose=True)
print(w.value)
print(v.value)
