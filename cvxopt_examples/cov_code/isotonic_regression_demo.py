import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.isotonic import IsotonicRegression
from sklearn.utils import check_random_state

n = 100
x = np.arange(n)
rs = check_random_state(0)
s = np.linspace(-np.pi / 3, 0.55 * np.pi, n)
y = rs.randint(-2, 2.5, size=(n)) + 20 * np.sin(s)

# Fit IsotonicRegression and LinearRegression models
ir = IsotonicRegression()
y_ = ir.fit_transform(x, y)
lr = LinearRegression()
lr.fit(x[:, np.newaxis], y)

plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['font.size'] = 24

plt.plot(x, y, 'b.', markersize=12, markerfacecolor='w', markeredgewidth=1.0)
plt.plot(x, y_, 'k-', markersize=6, linewidth=2.0, markeredgewidth=1.0)
plt.ylim([-20, 30])

plt.plot(x, y_, 'kx', markersize=8, linewidth=2.0, markeredgewidth=1.0)
plt.ylim([-20, 30])

plt.figure()
plt.plot(x, y, 'b.', markersize=12, markerfacecolor='w', markeredgewidth=1.0)
plt.plot(x, lr.predict(x[:, np.newaxis]), 'k-', linewidth=2.0)
plt.ylim([-20, 30])
plt.show()
