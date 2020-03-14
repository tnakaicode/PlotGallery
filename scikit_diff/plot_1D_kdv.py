r"""
One dimension Korteweg–de Vries study case.
===========================================

The `Korteweg–de Vries <https://en.wikipedia.org/wiki/Korteweg%E2%80%93de_Vries_equation>`_
equation is a non-linear PDE modeling wave on shallow water surfaces.
It reads

.. math::
    \frac{\partial U}{\partial t} + U\,\frac{\partial U}{\partial x} = a\,\frac{\partial^2 U}{\partial x^2} + b\,\frac{\partial^3 U}{\partial x^3}

The initial conditions is taken as a smoothed triangle. The discontinuity occuring usually in Burger equation results here
in a train of capillary wave after the wave front.

This example can be compeared with this `Dedalus Project example <https://dedalus-project.readthedocs
.io/en/latest/notebooks/dedalus_tutorial_problems_solvers.html>`_ where the same model is solved with
pseudo-spectral method.
"""

import numpy as np
import pylab as pl
from skfdiff import Model, Simulation

model = Model("-U * dxU + a * dxxU + b * dxxxU", "U(x)", ["a", "b"])

x = np.linspace(-2, 6, 1000)

n = 20
U = np.log(1 + np.cosh(n) ** 2 / np.cosh(n * x) ** 2) / (2 * n)

initial_fields = model.fields_template(x=x, U=U, a=2e-4, b=1e-4)

simulation = Simulation(model, initial_fields, dt=0.05, tmax=10)
container = simulation.attach_container()

simulation.run()
(
    container.data.U[: -2 : container.data.t.size // 6].plot(
        col="t", col_wrap=3, color="black"
    )
)
pl.show()
