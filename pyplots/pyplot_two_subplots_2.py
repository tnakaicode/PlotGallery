"""
===================
Pyplot Two Subplots
===================

Create a figure with two subplots with `pyplot.subplot`.
"""
import numpy as np
import matplotlib.pyplot as plt


def f(t):
    return np.log(t) * np.cos(2 * np.pi * t)


t1 = np.arange(0.0, 5.0, 0.1)
t2 = np.arange(0.0, 5.0, 0.02)

plt.figure()
plt.subplot(2, 1, 1)
plt.plot(t1, f(t1), color='tab:blue', marker='o')
plt.plot(t2, f(t2), color='black')

plt.subplot(2, 1, 2)
plt.plot(t2, np.cos(2 * np.pi * t2), color='tab:orange', linestyle='--')
plt.show()

#############################################################################
#
# ------------
#
# References
# """"""""""
#
# The use of the following functions, methods, classes and modules is shown
# in this example:

import matplotlib
matplotlib.pyplot.figure
matplotlib.pyplot.subplot
