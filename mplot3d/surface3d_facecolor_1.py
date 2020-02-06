import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.colors

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x = np.arange(3)
X, Y = np.meshgrid(x, x)
Z = np.ones_like(X)

V = np.array([[3, 2, 2], [1, 0, 3], [2, 1, 0]])

norm = matplotlib.colors.Normalize(vmin=0, vmax=3)
ax.plot_surface(X, Y, Z, facecolors=plt.cm.jet(norm(V)), shade=False)

m = cm.ScalarMappable(cmap=plt.cm.jet, norm=norm)
m.set_array([])
plt.colorbar(m)

ax.set_xlabel('x')
ax.set_ylabel('y')

plt.show()
