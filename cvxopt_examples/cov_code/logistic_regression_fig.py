import matplotlib.pyplot as plt
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

s1_min = min(S[0, :]) - 0.5
s1_max = max(S[1, :]) + 0.5
s2_min = -(v.value + (s1_min * w.value[0])) / w.value[1]
s2_max = -(v.value + (s2_min * w.value[0])) / w.value[1]
s1 = [s1_min, s1_max]
s2_min = s2_min.item(0)
s2_max = s2_max.item(0)
s2 = [s2_min, s2_max]

for i in range(0, S.shape[1]):
    if t[i] > 0:
        plt.scatter(S[0, i], S[1, i], marker='o', c='b')
    else:
        plt.scatter(S[0, i], S[1, i], marker='x', c='r')
plt.plot(s1, s2, c='k')
plt.show()
