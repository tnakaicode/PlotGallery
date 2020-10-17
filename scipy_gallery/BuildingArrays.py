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

# In[2]:


from numpy import *


# Arrays can be created from the usual python lists and tuples using the
# array function. For example,

# In[3]:


a = array([1,2,3])


# returns a one dimensional array of integers. The array instance has a
# large set of methods and properties attached to it. For example, is the
# dimension of the array. In this case, it would simply be .
# 
# One big difference between array objects and python's sequences object
# is the definition of the mathematical operators. Whereas the addition of
# two lists concatenates those list, the addition of two arrays adds the
# arrays element-wise. For example :

# In[4]:


b = array((10,11,12))
a + b


# Subtraction, multiplication and division are defined similarly.
# 
# A common gotcha for beginners is the type definition of arrays. Unless
# otherwise instructed, the array construct uses the type of its argument.
# Since was created from a list of integers, it is defined as an integer
# array, more precisely :

# In[5]:


a.dtype


# Accordingly, mathematical operations such as division will operate as
# usual in python, that is, will return an integer answer :

# In[6]:


a/3


# To obtain the expected answer, one solution is to force the casting of
# integers into real numbers by dividing by a real number . A more careful
# approach is to define the type at initialization time :

# In[7]:


a = array([1,2,3], dtype=float)


# Another way to cast is by using Numpy's built-in cast functions `astype`
# and `cast`. These allow you to change the type of data you're working
# with:

# In[8]:


a = array([1,2,3], dtype=int)
b = a.astype('float')


# The elements of an array are accessed using the bracket notation where
# is an integer index starting at 0. Sub-arrays can be accessed by using
# general indexes of the form `start:stop:step`. `a[start:stop:step]` will
# return a reference to a sub-array of array `a` starting with (including)
# the element at index `start` going up to (but not including) the
# element at index stop in steps of *step*. e.g.:

# In[9]:


data = array([0.5, 1.2, 2.2, 3.4, 3.5, 3.4, 3.4, 3.4], float)
t = arange(len(data), dtype='float') * 2*pi/(len(data)-1)
t[:]              # get all t-values


# In[10]:


t[2:4]            # get sub-array with the elements at the indexes 2,3


# In[11]:


t[slice(2,4)]     # the same using slice


# In[12]:


t[0:6:2]          # every even-indexed value up to but excluding 6


# Furthermore, there is the possibility to access array-elements using
# bool-arrays. The bool-array has the indexes of elements which are to be
# accessed set to *True.*

# In[13]:


i = array(len(t)*[False], bool)        # create an bool-array for indexing
i[2] = True; i[4] = True; i[6] = True  # we want elements with indexes 2,4 and 6
t[i]


# We can use this syntax to make slightly more elaborate constructs.
# Consider the `data[:]` and `t[:]` arrays defined before. Suppose we want to
# get the four (`t[i]/data[i]`)-pairs with the four `t[i]-values` being
# closest to a point `p=1.8`. We could proceed as follows:

# In[14]:


p=1.8                            # set our point
abs(t-p)                         # how much do the t[:]-values differ from p?


# In[15]:


dt_m = sort(abs(t-p))[3]         # how large is the 4-th largest absolute distance between the
                                 # t[:]-values and p


# In[16]:


abs(t-p) <= dt_m                 # where are the four elements of t[:]closest to p ?


# In[17]:


y_p = data[abs(t-p) <= dt_m]     # construct the sub-arrays; (1) get the 4 t[:]-values
t_p = t[abs(t-p) <= dt_m]        # (2) get the data t[:]-values corresponding to the 4 t[:] values
y_p


# In[18]:


t_p


# It has to be kept in mind that slicing returns a reference to the data.
# As a consequence, changes in the returned sub-array cause changes in the
# original array and vice versa. If one wants to copy only the values one
# can use the `copy()`-method of the matrix object. For example:

# In[19]:


# first lets define a 2-d matrix
A = array([[0,   1,  2,  3],   # initialize 2-d array
           [4,   5,  6,  7],
           [8,   9, 10, 11],
           [12, 13, 14, 15]])
A


# In[20]:


b=A[1:3,0:2]                    # let's get a sub-matrix containing the cross-section of
                                # rows 1,2 and columns 0,1
                                # !attention! this assigns to b a reference to the
                                # sub-matrix of A
b


# In[21]:


c=A[1:3,0:2].copy()             # copy the entries
c


# In[22]:


A[1:3,0:2] = 42                 # we can also assign by slicing (this also changes shallow copies)
b                               # b also affected (only a reference to sub matrix)


# In[23]:


c                               # still the same (deep copy)


# Matrix dot product
# ------------------
# 
# The next example creates two matrices: `a` and `b`, and computes the dot
# product `axb` (in other words, the standard matrix product)

# In[24]:


a = array([[1,2], [2,3]])
b = array([[7,1], [0,1]])
dot(a, b)


# As of Python 3.5, the `@` operator may be used for matrix multiplication:

# In[25]:


a @ b


# Automatic array creation
# ------------------------
# 
# SciPy (via Numpy) provides numerous ways to create arrays automatically.
# For example, to create a vector of evenly spaced numbers, the linspace
# function can be called. This is often useful to compute the result of a
# function on some domain. For example, to compute the value of the
# function on one period, we would define a vector going from 0 to 2 pi ($\pi$)
# and compute the value of the function for all values in this vector :

# In[26]:


x = linspace(0, 2*pi, 100)
y = sin(x)


# The same can be done on a N-dimensional grid using the class and some of
# its object creation methods. For example,

# In[27]:


x, y = mgrid[0:10:.1, 0:10:.2]


# returns two matrices, x and y, whose elements range from 0 to 10
# (non-inclusively) in .1 and .2 increments respectively. These matrices
# can be used to compute the value of a function at the points (x\_i,
# y\_i) defined by those grids :

# In[28]:


z = (x+y)**2


# The ogrid object has the exact same behavior, but instead of storing an
# N-D matrix into memory, it stores only the 1-D vector that defines it.
# For large matrices, this can lead to significant economy of memory
# space.
# 
# Other useful functions to create matrices are and who initialize arrays
# full of zeros and ones. Note that those will be float arrays by default.
# This may lead to curious behaviour for the unawares. For example, let's
# initialize a matrix with zeros, and then place values in it element by
# element.

# In[29]:


mz = zeros((2, 2), dtype=int)
mz[0, 0] = .5**2
mz[1, 1] = 1.6**2


# In this example, we are trying to store floating point numbers in an
# integer array. Thus, the numbers are then recast to integers, so that if
# we print the matrix, we obtain :

# In[30]:


mz


# To create real number arrays, one simply need to state the type
# explicitly in the call to the function :

# In[31]:


mz = zeros((2, 2), dtype=float)


# Repeating array segments
# ------------------------
# 
# The ndarray.repeat() method returns a new array with dimensions repeated
# from the old one.

# In[32]:


a = array([[0, 1],
       [2, 3]])
a.repeat(2, axis=0) # repeats each row twice in succession


# In[33]:


a.repeat(3, axis=1) # repeats each column 3 times in succession


# In[34]:


a.repeat(2, axis=None) # flattens (ravels), then repeats each element twice


# These can be combined to do some useful things, like enlarging image
# data stored in a 2D array:

# In[35]:


def enlarge(a, x=2, y=None):
    """Enlarges 2D image array a using simple pixel repetition in both dimensions.
    Enlarges by factor x horizontally and factor y vertically.
    If y is left as None, uses factor x for both dimensions."""
    a = asarray(a)
    assert a.ndim == 2
    if y == None:
        y = x
    for factor in (x, y):
        assert factor.__class__ == int
        assert factor > 0
    return a.repeat(y, axis=0).repeat(x, axis=1)

enlarge(a, x=2, y=2)

