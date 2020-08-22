"""
================================================================================
Create a rotating element
================================================================================

Create a rotating element.

"""

from math import pi

import matplotlib.pyplot as plt

import freshkiss3d as fk

element = fk.Rotating(angles_number = 5,
                      angular_velocity = 2*pi/48.,
                      phase = 2.*pi/32.)

for time in [0., 1., 2.]:
    element.rotates(time)
    print(time, element.angles)
    element.plot()

plt.legend()
plt.axis('scaled')
plt.xlim(-1.2, 1.2)
plt.ylim(-1.2, 1.2)
plt.show()
