"""
==========
Histograms
==========

Demonstrates how to plot histograms with matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

# Fixing random state for reproducibility
np.random.seed(19680801)


###############################################################################
# Generate data and plot a simple histogram
# -----------------------------------------
#
# To generate a 1D histogram we only need a single vector of numbers. For a 2D
# histogram we'll need a second vector. We'll generate both below, and show
# the histogram for each vector.

N_points = 100000
n_bins = 20

# Generate a normal distribution, center at x=0 and y=5
x = np.random.randn(N_points)
y = .4 * x + np.random.randn(100000) + 5

fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

# We can set the number of bins with the `bins` kwarg
axs[0].hist(x, bins=n_bins)
axs[1].hist(y, bins=n_bins)


###############################################################################
# Updating histogram colors
# -------------------------
#
# The histogram method returns (among other things) a ``patches`` object. This
# gives us access to the properties of the objects drawn. Using this, we can
# edit the histogram to our liking. Let's change the color of each bar
# based on its y value.

fig, axs = plt.subplots(1, 2, tight_layout=True)

# N is the count in each bin, bins is the lower-limit of the bin
N, bins, patches = axs[0].hist(x, bins=n_bins)

# We'll color code by height, but you could use any scalar
fracs = N / N.max()

# we need to normalize the data to 0..1 for the full range of the colormap
norm = colors.Normalize(fracs.min(), fracs.max())

# Now, we'll loop through our objects and set the color of each accordingly
for thisfrac, thispatch in zip(fracs, patches):
    color = plt.cm.viridis(norm(thisfrac))
    thispatch.set_facecolor(color)

# We can also normalize our inputs by the total number of counts
axs[1].hist(x, bins=n_bins, density=True)

# Now we format the y-axis to display percentage
axs[1].yaxis.set_major_formatter(PercentFormatter(xmax=1))


###############################################################################
# Plot a 2D histogram
# -------------------
#
# To plot a 2D histogram, one only needs two vectors of the same length,
# corresponding to each axis of the histogram.

fig, ax = plt.subplots(tight_layout=True)
hist = ax.hist2d(x, y)


###############################################################################
# Customizing your histogram
# --------------------------
#
# Customizing a 2D histogram is similar to the 1D case, you can control
# visual components such as the bin size or color normalization.

fig, axs = plt.subplots(3, 1, figsize=(5, 15), sharex=True, sharey=True,
                        tight_layout=True)

# We can increase the number of bins on each axis
axs[0].hist2d(x, y, bins=40)

# As well as define normalization of the colors
axs[1].hist2d(x, y, bins=40, norm=colors.LogNorm())

# We can also define custom numbers of bins for each axis
axs[2].hist2d(x, y, bins=(80, 10), norm=colors.LogNorm())

plt.show()
