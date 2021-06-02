import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D


def plot_3D_array_slices(array):
    min_val = array.min()
    max_val = array.max()
    n_x, n_y, n_z = array.shape
    colormap = plt.cm.YlOrRd

    x_cut = array[n_x // 2, :, :]
    Y, Z = np.mgrid[0:n_y, 0:n_z]
    X = n_x // 2 * np.ones((n_y, n_z))
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=colormap(
        (x_cut - min_val) / (max_val - min_val)), shade=False)
    ax.set_title("x slice")

    y_cut = array[:, n_y // 2, :]
    X, Z = np.mgrid[0:n_x, 0:n_z]
    Y = n_y // 2 * np.ones((n_x, n_z))
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=colormap(
        (y_cut - min_val) / (max_val - min_val)), shade=False)
    ax.set_title("y slice")

    z_cut = array[:, :, n_z // 2]
    X, Y = np.mgrid[0:n_x, 0:n_y]
    Z = n_z // 2 * np.ones((n_x, n_y))
    #fig = plt.figure()
    #ax = fig.add_subplot(111, projection='3d')
    ax.plot_surface(X, Y, Z, rstride=1, cstride=1, facecolors=colormap(
        (z_cut - min_val) / (max_val - min_val)), shade=False)
    ax.set_title("z slice")

    plt.show()


n_pts = 100
r_square = (np.mgrid[-1:1:1j * n_pts, -1:1:1j *
            n_pts, -1:1:1j * n_pts]**2).sum(0)
plot_3D_array_slices(r_square)
