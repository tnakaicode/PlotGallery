#!/usr/bin/env python
# coding: utf-8

# Building arrays
# ========
#
# This is a brief introduction to array objects, their declaration and use
# in SciPy. A comprehensive list of examples of Numpy functions for arrays
# can be found at [Numpy Example List With Doc](http://wiki.scipy.org/Numpy_Example_List_With_Doc)
#
# Basics
# ------
#
# Numerical arrays are not yet defined in the standard Python language. To
# load the array object and its methods into the namespace, the Numpy
# package must be imported:


import numpy as np

# Repeating array segments
# ------------------------
#
# The ndarray.repeat() method returns a new array with dimensions repeated
# from the old one.


a = np.array([[0, 1],
              [2, 3]])
a.repeat(2, axis=0)  # repeats each row twice in succession


a.repeat(3, axis=1)  # repeats each column 3 times in succession

a.repeat(2, axis=None)  # flattens (ravels), then repeats each element twice


# These can be combined to do some useful things, like enlarging image
# data stored in a 2D array:


def enlarge(a, x=2, y=None):
    """Enlarges 2D image array a using simple pixel repetition in both dimensions.
    Enlarges by factor x horizontally and factor y vertically.
    If y is left as None, uses factor x for both dimensions."""
    a = np.asarray(a)
    assert a.ndim == 2
    if y == None:
        y = x
    for factor in (x, y):
        assert factor.__class__ == int
        assert factor > 0
    return a.repeat(y, axis=0).repeat(x, axis=1)


print(enlarge(a, x=2, y=2))
