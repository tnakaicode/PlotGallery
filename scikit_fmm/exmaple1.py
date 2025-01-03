import numpy as np
import matplotlib.pyplot as plt
import skfmm

X, Y = np.meshgrid(np.linspace(-1, 1, 201), np.linspace(-1, 1, 201))
phi = -1 * np.ones_like(X)

phi[X > -0.5] = 1
phi[np.logical_and(np.abs(Y) < 0.25, X > -0.75)] = 1
plt.figure()
plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
plt.title('Boundary location: the zero contour of phi')
plt.savefig('./exmaple1_2d_phi.png')

d = skfmm.distance(phi, dx=1e-2)
plt.figure()
plt.title('Distance from the boundary')
plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
plt.contour(X, Y, d, 15)
plt.colorbar()
plt.savefig('./exmaple1_2d_phi_distance.png')

speed = np.ones_like(X)
speed[Y > 0] = 1.5
t = skfmm.travel_time(phi, speed, dx=1e-2)
plt.figure()
plt.title('Travel time from the boundary')
plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
plt.contour(X, Y, t, 15)
plt.colorbar()
plt.savefig('./exmaple1_2d_phi_travel_time.png')

mask = np.logical_and(abs(X) < 0.1, abs(Y) < 0.5)
phi = np.ma.MaskedArray(phi, mask)
t = skfmm.travel_time(phi, speed, dx=1e-2)
plt.figure()
plt.title('Travel time from the boundary with an obstacle')
plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
plt.contour(X, Y, phi.mask, [0], linewidths=(3), colors='red')
plt.contour(X, Y, t, 15)
plt.colorbar()
plt.savefig('./exmaple1_2d_phi_travel_time_mask.png')

phi = -1 * np.ones_like(X)
phi[X > -0.5] = 1
phi[np.logical_and(np.abs(Y) < 0.25, X > -0.75)] = 1
d = skfmm.distance(phi, dx=1e-2, narrow=0.3)
plt.figure()
plt.title('Distance calculation limited to narrow band')
plt.contour(X, Y, phi, [0], linewidths=(3), colors='black')
plt.contour(X, Y, d, 15)
plt.colorbar()
plt.savefig('./exmaple1_2d_phi_distance_narrow.png')
plt.show()
