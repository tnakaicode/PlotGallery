# https://www.cvxpy.org/tutorial/intro/index.html
import cvxpy as cp
import numpy as np

# Problem data.
m = 10
n = 5
np.random.seed(1)
A = np.random.randn(m, n)
b = np.random.randn(m)

# Construct the problem.
x = cp.Variable(n)
objective = cp.Minimize(cp.sum_squares(A @ x - b))
constraints = [0 <= x, x <= 1]
prob = cp.Problem(objective, constraints)
prob.solve(verbose=True)

print("Optimal value", prob.value)
print("Optimal var")
print(x.value)
