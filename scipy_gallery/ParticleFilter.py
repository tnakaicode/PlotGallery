#!/usr/bin/env python
# coding: utf-8

# Particle filter
# ===============
#
# A basic particle filter tracking algorithm, using a uniformly
# distributed step as motion model, and the initial target colour as
# determinant feature for the weighting function. This requires an
# approximately uniformly coloured object, which moves at a speed no
# larger than stepsize per frame.
#
# This implementation assumes that the video stream is a sequence of numpy
# arrays, an iterator pointing to such a sequence or a generator
# generating one. The particle filter itself is a generator to allow for
# operating on real-time video streams.


#!python
from numpy import *
from numpy.random import *


def resample(weights):
    n = len(weights)
    indices = []
    C = [0.] + [sum(weights[:i + 1]) for i in range(n)]
    u0, j = random(), 0
    for u in [(u0 + i) / n for i in range(n)]:
        while u > C[j]:
            j += 1
        indices.append(j - 1)
    return indices


def particlefilter(sequence, pos, stepsize, n):
    seq = iter(sequence)
    x = ones((n, 2), int) * pos                   # Initial position
    f0 = seq.next()[tuple(pos)] * ones(n)         # Target colour model
    # Return expected position, particles and weights
    yield pos, x, ones(n) / n
    for im in seq:
        np.add(x, uniform(-stepsize, stepsize, x.shape), out=x,
               casting="unsafe")  # Particle motion model: uniform step
        # Clip out-of-bounds particles
        x = x.clip(zeros(2), array(im.shape) - 1).astype(int)
        f = im[tuple(x.T)]                         # Measure particle colours
        # Weight~ inverse quadratic colour distance
        w = 1. / (1. + (f0 - f)**2)
        w /= sum(w)                                 # Normalize w
        # Return expected position, particles and weights
        yield sum(x.T * w, axis=1), x, w
        # If particle cloud degenerate:
        if 1. / sum(w**2) < n / 2.:
            # Resample particles according to weights
            x = x[resample(w), :]


# The following code shows the tracker operating on a test sequence
# featuring a moving square against a uniform background.


#!python
if __name__ == "__main__":
    from pylab import *
    from itertools import izip
    import time

    ion()
    # Create an image sequence of 20 frames long
    seq = [im for im in zeros((20, 240, 320), int)]
    # Add a square with starting position x0 moving along trajectory xs
    x0 = array([120, 160])
    xs = vstack((arange(20) * 3, arange(20) * 2)).T + x0
    for t, x in enumerate(xs):
        xslice = slice(x[0] - 8, x[0] + 8)
        yslice = slice(x[1] - 8, x[1] + 8)
        seq[t][xslice, yslice] = 255

    # Track the square through the sequence
    for im, p in izip(seq, particlefilter(seq, x0, 8, 100)):
        pos, xs, ws = p
        position_overlay = zeros_like(im)
        position_overlay[np.array(pos).astype(int)] = 1
        particle_overlay = zeros_like(im)
        particle_overlay[tuple(xs.T)] = 1
        draw()
        time.sleep(0.3)
        # Causes flickering, but without the spy plots aren't overwritten
        clf()
        imshow(im, cmap="jet")                         # Plot the image
        # Plot the expected position
        spy(position_overlay, marker='.', color='b')
        spy(particle_overlay, marker=',', color='r')    # Plot the particles
