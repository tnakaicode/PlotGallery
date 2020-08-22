"""
================================================================================
Time dependent flowrate
================================================================================

Define a time dependant flowrate

"""

import matplotlib.pyplot as plt
import numpy as np

import freshkiss3d as fk

times = [5., 11., 14., 17.]
flowrates = [0., 20., 20., 10.]

tdd = fk.TimeDependentFlowRate(times, flowrates)

simu_times = np.linspace(0, 20, 41)
simu_flowrates = [tdd.interpolate(t) for t in simu_times]

plt.plot(times, flowrates, 'ro')
plt.plot(simu_times, simu_flowrates, 'bx')
plt.xlim(-5, 25)
plt.ylim(-5, 25)
plt.xlabel('time')
plt.ylabel('flowrate')
plt.grid()
plt.show()
