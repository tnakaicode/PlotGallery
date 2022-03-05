#!/usr/bin/env python
# coding: utf-8

# Matplotlib: converting a matrix to a raster image
# ======================================================================
#
# Scipy provides a command (imsave) to make a raster (png, jpg...) image
# from a 2D array, each pixel corresponding to one value of the array. Yet
# the image is black and white.
#
# Here is a recipy to do this with Matplotlib, and use a colormap to give
# color to the image.


import numpy as np
from matplotlib.pyplot import *
from scipy import mgrid


def imsave(filename, X, **kwargs):
    """ Homebrewed imsave to have nice colors... """
    figsize = (np.array(X.shape) / 100.0)[::-1]
    # rcParams.update({'figure.figsize':figsize})
    fig = figure(figsize=figsize)
    axes([0, 0, 1, 1])  # Make the plot occupy the whole canvas
    axis('off')
    fig.set_size_inches(figsize)
    imshow(X, origin='lower', **kwargs)
    savefig(filename, facecolor='black', edgecolor='black', dpi=100)
    close(fig)


X, Y = mgrid[-5:5:0.1, -5:5:0.1]
Z = np.sin(X**2 + Y**2 + 1e-4) / (X**2 + Y**2 +
                                  1e-4)  # Create the data to be plotted
imsave('imsave.png', Z, cmap=cm.hot)


imshow(imread('imsave.png'))
show()
