#!/usr/bin/env python
# coding: utf-8

# Stride tricks for the Game of Life
# ==================================
#
# This is similar to [:../SegmentAxis:Segment axis], but for 2D arrays
# with 2D windows.
#
# The Game of Life is a cellular automaton devised by the British
# mathematician John Horton Conway in 1970, see [1].
#
# It consists of a rectangular grid of cells which are either dead or
# alive, and a transition rule for updating the cells' state. To update
# each cell in the grid, the state of the 8 neighbouring cells needs to be
# examined, i.e. it would be desirable to have an easy way of accessing
# the 8 neighbours of all the cells at once without making unnecessary
# copies. The code snippet below shows how to use the devious stride
# tricks for that purpose.
#
# [1] [Game of Life](http://en.wikipedia.org/wiki/Conway%27s_Game_of_Life)
# at Wikipedia


import numpy as np
from numpy.lib import stride_tricks
x = np.arange(20).reshape([4, 5])
xx = stride_tricks.as_strided(
    x, shape=(2, 3, 3, 3), strides=x.strides + x.strides)


print(x)


print(xx)


print(xx[0, 0])


print(xx[1, 2])


print(x.strides)


print(xx.strides)
