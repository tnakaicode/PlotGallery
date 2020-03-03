# https://www.cvxpy.org/tutorial/intro/index.html
import cvxpy as cp
import numpy as np

# Create two scalar optimization variables.
x = cp.Variable()
y = cp.Variable()

print(x, y)
# Create two constraints.
constraints = [x + y == 1,
               x - y >= 1]

# Form objective.
obj = cp.Minimize((x - y)**2)

# Form and solve problem.
prob = cp.Problem(obj, constraints)
prob.solve()  # Returns the optimal value.
print("status:", prob.status)
print("optimal value", prob.value)
print("optimal var", x.value, y.value)

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

print(A, b)
print("Optimal value", prob.solve())
print("Optimal var")
print(x.value)

# Construct the problem.
np.random.seed(1)
A = np.random.randn(m, n)
b = np.random.randn(m)
x = cp.Variable(n)
objective = cp.Minimize(cp.norm(x, 1))
constraints = [A@x == b]
prob = cp.Problem(objective, constraints)

print(A, b)
print("Optimal value", prob.solve())
print("Optimal var")
print(x.value)

m = 5
n = 10
np.random.seed(1)
A = np.random.randn(m, n)
b = np.random.randn(m)

# Construct the problem.
x = cp.Variable(n)
objective = cp.Minimize(cp.sum_squares(A @ x - b))
constraints = [0 <= x, x <= 1]
prob = cp.Problem(objective, constraints)

print(A, b)
print("Optimal value", prob.solve())
print("Optimal var")
print(x.value)

m = 600
n = 1000
np.random.seed(1)
A = np.random.randn(m, n)
b = np.random.randn(m)

# Construct the problem.
x = cp.Variable(n)
objective = cp.Minimize(cp.sum_squares(A @ x - b))
constraints = [0 <= x, x <= 1]
prob = cp.Problem(objective, constraints)

print(A, b)
print("Optimal value", prob.solve())
