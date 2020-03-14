"""
Two dimension acoustic waves simulation.
========================================

Thank to Matteo Ravasi (@mrava87) for this example.

This example show the propagation of a 2D acoustic wave across
two different medium with different sound speed / density.

The wave start as a source as a signal in time at a given location
in space. This source is inserted via a hook function.
"""

import numpy as np
import matplotlib.pyplot as plt

from scipy.ndimage import gaussian_filter
from skfdiff import Model, Simulation

from collections import defaultdict


def hook(t, fields):
    f0 = 40
    t0 = 0.01
    q = np.zeros_like(fields.P)
    q[20, ny // 2] = (1 - 2 * (np.pi * f0 * (t - t0)) ** 2) * np.exp(
        -(np.pi * f0 * (t - t0)) ** 2
    )
    fields["q"] = ("x", "y"), gaussian_filter(q, sigma=2)
    return fields


bc = defaultdict(lambda: ("dirichlet", "dirichlet"))

model = Model(
    [
        "-upwind(1/rho, P, x, 1)",
        "-upwind(1/rho, P, y, 1)",
        "upwind(-1/k, Vx, x, 1) + upwind(-1/k, Vy, y, 1) + q",
    ],
    ["Vx(x, y)", "Vy(x, y)", "P(x, y)"],
    parameters=["rho(x, y)", "k(x, y)", "q(x, y)"],
    boundary_conditions=bc,
)


nx = ny = 256
x = np.linspace(-200, 200, nx)
y = np.linspace(-200, 200, ny)
xx, yy = np.meshgrid(x, y, indexing="ij")

dt = 1e-3
tmax = 0.15
U = np.zeros((nx, ny))
q = np.zeros((nx, ny))
c = 1800 * np.ones((nx, ny))
c[nx // 3 :] = 3000
rho = 1000 * np.ones((nx, ny))
rho[nx // 3 :] = 4000
k = 1 / (c ** 2 * rho)

# We fill the fields container
initial_fields = model.Fields(x=x, y=y, P=U, Vx=U, Vy=U, q=q, k=k, rho=rho)

# We initialize the simulation
simulation = Simulation(
    model,
    initial_fields,
    dt=dt,
    tol=1e-1,
    tmax=tmax,
    hook=hook,
    solver="iteratif",
    time_stepping=True,
)

container_acoustic = simulation.attach_container()
simulation.run()

facet = container_acoustic.data.P[::30].T.plot(
    col="t", col_wrap=3, cmap="seismic", vmin=-3e-5, vmax=3e-5
)
for ax in facet.axes.flatten():
    left_domain = plt.Polygon(
        [
            (x.min(), y.min()),
            (x[nx // 3], y.min()),
            (x[nx // 3], y.max()),
            (x.min(), y.max()),
        ],
        color="blue",
        alpha=0.2,
    )
    right_domain = plt.Polygon(
        [
            (x[nx // 3], y.min()),
            (x.max(), y.min()),
            (x.max(), y.max()),
            (x[nx // 3], y.max()),
        ],
        color="red",
        alpha=0.2,
    )
    ax.add_patch(left_domain)
    ax.add_patch(right_domain)
plt.savefig("2D_acoustic.png")
###############################################################################
# .. image:: ../../_static/2D_acoustic.png
#
