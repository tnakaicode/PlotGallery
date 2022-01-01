#!/usr/bin/env python
# coding: utf-8

# ## Applying unvectorized functions with `apply_ufunc`

# This example will illustrate how to conveniently apply an unvectorized function `func` to xarray objects using `apply_ufunc`. `func` expects 1D numpy arrays and returns a 1D numpy array. Our goal is to coveniently apply this function along a dimension of xarray objects that may or may not wrap dask arrays with a signature.
#
# We will illustrate this using `np.interp`:
#
#     Signature: np.interp(x, xp, fp, left=None, right=None, period=None)
#     Docstring:
#         One-dimensional linear interpolation.
#
#     Returns the one-dimensional piecewise linear interpolant to a function
#     with given discrete data points (`xp`, `fp`), evaluated at `x`.
#
# and write an `xr_interp` function with signature
#
#     xr_interp(xarray_object, dimension_name, new_coordinate_to_interpolate_to)
#
# ### Load data
#
# First lets load an example dataset


import xarray as xr
import numpy as np

xr.set_options(display_style="html")  # fancy HTML repr

air = (
    xr.tutorial.load_dataset("air_temperature")
    .air.sortby("lat")  # np.interp needs coordinate in ascending order
    .isel(time=slice(4), lon=slice(3))
)  # choose a small subset for convenience


# The function we will apply is `np.interp` which expects 1D numpy arrays. This functionality is already implemented in xarray so we use that capability to make sure we are not making mistakes.


newlat = np.linspace(15, 75, 100)
air.interp(lat=newlat)


# Let's define a function that works with one vector of data along `lat` at a time.


def interp1d_np(data, x, xi):
    return np.interp(xi, x, data)


interped = interp1d_np(air.isel(time=0, lon=0), air.lat, newlat)
expected = air.interp(lat=newlat)

# no errors are raised if values are equal to within floating point precision
np.testing.assert_allclose(expected.isel(time=0, lon=0).values, interped)


# ### No errors are raised so our interpolation is working.
#
# This function consumes and returns numpy arrays, which means we need to do a lot of work to convert the result back to an xarray object with meaningful metadata. This is where `apply_ufunc` is very useful.
#
# ### `apply_ufunc`
#
#     Apply a vectorized function for unlabeled arrays on xarray objects.
#
#     The function will be mapped over the data variable(s) of the input arguments using
#     xarray’s standard rules for labeled computation, including alignment, broadcasting,
#     looping over GroupBy/Dataset variables, and merging of coordinates.
#
# `apply_ufunc` has many capabilities but for simplicity this example will focus on the common task of vectorizing 1D functions over nD xarray objects. We will iteratively build up the right set of arguments to `apply_ufunc` and read through many error messages in doing so.


xr.apply_ufunc(
    interp1d_np,  # first the function
    # now arguments in the order expected by 'interp1_np'
    air.isel(time=0, lon=0),
    air.lat,
    newlat,
)


# `apply_ufunc` needs to know a lot of information about what our function does so that it can reconstruct the outputs. In this case, the size of dimension lat has changed and we need to explicitly specify that this will happen. xarray helpfully tells us that we need to specify the kwarg `exclude_dims`.

# ### `exclude_dims`

#
# ```
# exclude_dims : set, optional
#         Core dimensions on the inputs to exclude from alignment and
#         broadcasting entirely. Any input coordinates along these dimensions
#         will be dropped. Each excluded dimension must also appear in
#         ``input_core_dims`` for at least one argument. Only dimensions listed
#         here are allowed to change size between input and output objects.
# ```


xr.apply_ufunc(
    interp1d_np,  # first the function
    # now arguments in the order expected by 'interp1_np'
    air.isel(time=0, lon=0),
    air.lat,
    newlat,
    # dimensions allowed to change size. Must be set!
    exclude_dims=set(("lat",)),
)


# ### Core dimensions
#
#

# Core dimensions are central to using `apply_ufunc`. In our case, our function expects to receive a 1D vector along `lat` &#x2014; this is the dimension that is "core" to the function's functionality. Multiple core dimensions are possible. `apply_ufunc` needs to know which dimensions of each variable are core dimensions.
#
#     input_core_dims : Sequence[Sequence], optional
#         List of the same length as ``args`` giving the list of core dimensions
#         on each input argument that should not be broadcast. By default, we
#         assume there are no core dimensions on any input arguments.
#
#         For example, ``input_core_dims=[[], ['time']]`` indicates that all
#         dimensions on the first argument and all dimensions other than 'time'
#         on the second argument should be broadcast.
#
#         Core dimensions are automatically moved to the last axes of input
#         variables before applying ``func``, which facilitates using NumPy style
#         generalized ufuncs [2]_.
#
#     output_core_dims : List[tuple], optional
#         List of the same length as the number of output arguments from
#         ``func``, giving the list of core dimensions on each output that were
#         not broadcast on the inputs. By default, we assume that ``func``
#         outputs exactly one array, with axes corresponding to each broadcast
#         dimension.
#
#         Core dimensions are assumed to appear as the last dimensions of each
#         output in the provided order.
#
# Next we specify `"lat"` as `input_core_dims` on both `air` and `air.lat`


xr.apply_ufunc(
    interp1d_np,  # first the function
    # now arguments in the order expected by 'interp1_np'
    air.isel(time=0, lon=0),
    air.lat,
    newlat,
    input_core_dims=[["lat"], ["lat"], []],
    # dimensions allowed to change size. Must be set!
    exclude_dims=set(("lat",)),
)


# xarray is telling us that it expected to receive back a numpy array with 0 dimensions but instead received an array with 1 dimension corresponding to `newlat`. We can fix this by specifying `output_core_dims`


xr.apply_ufunc(
    interp1d_np,  # first the function
    # now arguments in the order expected by 'interp1_np'
    air.isel(time=0, lon=0),
    air.lat,
    newlat,
    input_core_dims=[["lat"], ["lat"], []],  # list with one entry per arg
    output_core_dims=[["lat"]],
    # dimensions allowed to change size. Must be set!
    exclude_dims=set(("lat",)),
)


# Finally we get some output! Let's check that this is right
#
#


interped = xr.apply_ufunc(
    interp1d_np,  # first the function
    # now arguments in the order expected by 'interp1_np'
    air.isel(time=0, lon=0),
    air.lat,
    newlat,
    input_core_dims=[["lat"], ["lat"], []],  # list with one entry per arg
    output_core_dims=[["lat"]],
    # dimensions allowed to change size. Must be set!
    exclude_dims=set(("lat",)),
)
interped["lat"] = newlat  # need to add this manually
xr.testing.assert_allclose(expected.isel(time=0, lon=0), interped)


# No errors are raised so it is right!

# ### Vectorization with `np.vectorize`

# Now  our function currently only works on one vector of data which is not so useful given our 3D dataset.
# Let's try passing the whole dataset. We add a `print` statement so we can see what our function receives.


def interp1d_np(data, x, xi):
    print(f"data: {data.shape} | x: {x.shape} | xi: {xi.shape}")
    return np.interp(xi, x, data)


interped = xr.apply_ufunc(
    interp1d_np,  # first the function
    air.isel(
        lon=slice(3), time=slice(4)
    ),  # now arguments in the order expected by 'interp1_np'
    air.lat,
    newlat,
    input_core_dims=[["lat"], ["lat"], []],  # list with one entry per arg
    output_core_dims=[["lat"]],
    # dimensions allowed to change size. Must be set!
    exclude_dims=set(("lat",)),
)
interped["lat"] = newlat  # need to add this manually
xr.testing.assert_allclose(expected.isel(time=0, lon=0), interped)


# That's a hard-to-interpret error but our `print` call helpfully printed the shapes of the input data:
#
#     data: (10, 53, 25) | x: (25,) | xi: (100,)
#
# We see that `air` has been passed as a 3D numpy array which is not what `np.interp` expects. Instead we want loop over all combinations of `lon` and `time`; and apply our function to each corresponding vector of data along `lat`.
# `apply_ufunc` makes this easy by specifying `vectorize=True`:
#
#     vectorize : bool, optional
#         If True, then assume ``func`` only takes arrays defined over core
#         dimensions as input and vectorize it automatically with
#         :py:func:`numpy.vectorize`. This option exists for convenience, but is
#         almost always slower than supplying a pre-vectorized function.
#         Using this option requires NumPy version 1.12 or newer.
#
# Also see the documentation for `np.vectorize`: https://docs.scipy.org/doc/numpy/reference/generated/numpy.vectorize.html. Most importantly
#
#     The vectorize function is provided primarily for convenience, not for performance.
#     The implementation is essentially a for loop.


def interp1d_np(data, x, xi):
    print(f"data: {data.shape} | x: {x.shape} | xi: {xi.shape}")
    return np.interp(xi, x, data)


interped = xr.apply_ufunc(
    interp1d_np,  # first the function
    air,  # now arguments in the order expected by 'interp1_np'
    air.lat,  # as above
    newlat,  # as above
    input_core_dims=[["lat"], ["lat"], []],  # list with one entry per arg
    output_core_dims=[["lat"]],  # returned data has one dimension
    # dimensions allowed to change size. Must be set!
    exclude_dims=set(("lat",)),
    vectorize=True,  # loop over non-core dims
)
interped["lat"] = newlat  # need to add this manually
xr.testing.assert_allclose(expected, interped)


# This unfortunately is another cryptic error from numpy.
#
# Notice that `newlat` is not an xarray object. Let's add a dimension name `new_lat` and modify the call. Note this cannot be `lat` because xarray expects dimensions to be the same size (or broadcastable) among all inputs. `output_core_dims` needs to be modified appropriately. We'll manually rename `new_lat` back to `lat` for easy checking.


def interp1d_np(data, x, xi):
    print(f"data: {data.shape} | x: {x.shape} | xi: {xi.shape}")
    return np.interp(xi, x, data)


interped = xr.apply_ufunc(
    interp1d_np,  # first the function
    air,  # now arguments in the order expected by 'interp1_np'
    air.lat,  # as above
    newlat,  # as above
    # list with one entry per arg
    input_core_dims=[["lat"], ["lat"], ["new_lat"]],
    output_core_dims=[["new_lat"]],  # returned data has one dimension
    # dimensions allowed to change size. Must be a set!
    exclude_dims=set(("lat",)),
    vectorize=True,  # loop over non-core dims
)
interped = interped.rename({"new_lat": "lat"})
interped["lat"] = newlat  # need to add this manually
xr.testing.assert_allclose(
    expected.transpose(*interped.dims), interped  # order of dims is different
)


# Notice that the printed input shapes are all 1D and correspond to one vector along the `lat` dimension.
#
# The result is now an xarray object with coordinate values copied over from `data`. This is why `apply_ufunc` is so convenient; it takes care of a lot of boilerplate necessary to apply functions that consume and produce numpy arrays to xarray objects.
#
# One final point: `lat` is now the *last* dimension in `interped`. This is a "property" of core dimensions: they are moved to the end before being sent to `interp1d_np` as was noted in the docstring for `input_core_dims`
#
#         Core dimensions are automatically moved to the last axes of input
#         variables before applying ``func``, which facilitates using NumPy style
#         generalized ufuncs [2]_.

# ### Parallelization with dask
#
#

# So far our function can only handle numpy arrays. A real benefit of `apply_ufunc` is the ability to easily parallelize over dask chunks _when needed_.
#
# We want to apply this function in a vectorized fashion over each chunk of the dask array. This is possible using dask's `blockwise` or `map_blocks`. `apply_ufunc` wraps `blockwise` and asking it to map the function over chunks using `blockwise` is as simple as specifying `dask="parallelized"`. With this level of flexibility we need to provide dask with some extra information:
#   1. `output_dtypes`: dtypes of all returned objects, and
#   2. `output_sizes`: lengths of any new dimensions.
#
# Here we need to specify `output_dtypes` since `apply_ufunc` can infer the size of the new dimension `new_lat` from the argument corresponding to the third element in `input_core_dims`. Here I choose the chunk sizes to illustrate that `np.vectorize` is still applied so that our function receives 1D vectors even though the blocks are 3D.


def interp1d_np(data, x, xi):
    print(f"data: {data.shape} | x: {x.shape} | xi: {xi.shape}")
    return np.interp(xi, x, data)


interped = xr.apply_ufunc(
    interp1d_np,  # first the function
    air.chunk(
        {"time": 2, "lon": 2}
    ),  # now arguments in the order expected by 'interp1_np'
    air.lat,  # as above
    newlat,  # as above
    # list with one entry per arg
    input_core_dims=[["lat"], ["lat"], ["new_lat"]],
    output_core_dims=[["new_lat"]],  # returned data has one dimension
    # dimensions allowed to change size. Must be a set!
    exclude_dims=set(("lat",)),
    vectorize=True,  # loop over non-core dims
    dask="parallelized",
    output_dtypes=[air.dtype],  # one per output
).rename({"new_lat": "lat"})
interped["lat"] = newlat  # need to add this manually
xr.testing.assert_allclose(expected.transpose(*interped.dims), interped)


# Yay! our function is receiving 1D vectors, so we've successfully parallelized applying a 1D function over a block. If you have a distributed dashboard up, you should see computes happening as equality is checked.
#
#

# ### High performance vectorization: gufuncs, numba & guvectorize
#
#

# `np.vectorize` is a very convenient function but is unfortunately slow. It is only marginally faster than writing a for loop in Python and looping. A common way to get around this is to write a base interpolation function that can handle nD arrays in a compiled language like Fortran and then pass that to `apply_ufunc`.
#
# Another option is to use the numba package which provides a very convenient `guvectorize` decorator: https://numba.pydata.org/numba-doc/latest/user/vectorize.html#the-guvectorize-decorator
#
# Any decorated function gets compiled and will loop over any non-core dimension in parallel when necessary. We need to specify some extra information:
#
#    1. Our function cannot return a variable any more. Instead it must receive a variable (the last argument) whose contents the function will modify. So we change from `def interp1d_np(data, x, xi)` to `def interp1d_np_gufunc(data, x, xi, out)`. Our computed results must be assigned to `out`. All values of `out` must be assigned explicitly.
#
#    2. `guvectorize` needs to know the dtypes of the input and output. This is specified in string form as the first argument. Each element of the tuple corresponds to each argument of the function. In this case, we specify `float64` for all inputs and outputs: `"(float64[:], float64[:], float64[:], float64[:])"` corresponding to `data, x, xi, out`
#
#    3. Now we need to tell numba the size of the dimensions the function takes as inputs and returns as output i.e. core dimensions. This is done in symbolic form i.e. `data` and `x` are vectors of the same length, say `n`; `xi` and the output `out` have a different length, say `m`. So the second argument is (again as a string)
#          `"(n), (n), (m) -> (m)."` corresponding again to `data, x, xi, out`
#


from numba import float64, guvectorize


@guvectorize("(float64[:], float64[:], float64[:], float64[:])", "(n), (n), (m) -> (m)")
def interp1d_np_gufunc(data, x, xi, out):
    # numba doesn't really like this.
    # seem to support fstrings so do it the old way
    print(
        "data: " + str(data.shape) + " | x:" +
        str(x.shape) + " | xi: " + str(xi.shape)
    )
    out[:] = np.interp(xi, x, data)
    # gufuncs don't return data
    # instead you assign to a the last arg
    # return np.interp(xi, x, data)


# The warnings are about object-mode compilation relating to the `print` statement. This means we don't get much speed up: https://numba.pydata.org/numba-doc/latest/user/performance-tips.html#no-python-mode-vs-object-mode. We'll keep the `print` statement temporarily to make sure that `guvectorize` acts like we want it to.


interped = xr.apply_ufunc(
    interp1d_np_gufunc,  # first the function
    air.chunk(
        {"time": 2, "lon": 2}
    ),  # now arguments in the order expected by 'interp1_np'
    air.lat,  # as above
    newlat,  # as above
    # list with one entry per arg
    input_core_dims=[["lat"], ["lat"], ["new_lat"]],
    output_core_dims=[["new_lat"]],  # returned data has one dimension
    # dimensions allowed to change size. Must be a set!
    exclude_dims=set(("lat",)),
    # vectorize=True,  # not needed since numba takes care of vectorizing
    dask="parallelized",
    output_dtypes=[air.dtype],  # one per output
).rename({"new_lat": "lat"})
interped["lat"] = newlat  # need to add this manually
xr.testing.assert_allclose(expected.transpose(*interped.dims), interped)


# Yay! Our function is receiving 1D vectors and is working automatically with dask arrays. Finally let's comment out the print line and wrap everything up in a nice reusable function


from numba import float64, guvectorize


@guvectorize(
    "(float64[:], float64[:], float64[:], float64[:])",
    "(n), (n), (m) -> (m)",
    nopython=True,
)
def interp1d_np_gufunc(data, x, xi, out):
    out[:] = np.interp(xi, x, data)


def xr_interp(data, dim, newdim):

    interped = xr.apply_ufunc(
        interp1d_np_gufunc,  # first the function
        data,  # now arguments in the order expected by 'interp1_np'
        data[dim],  # as above
        newdim,  # as above
        # list with one entry per arg
        input_core_dims=[[dim], [dim], ["__newdim__"]],
        output_core_dims=[["__newdim__"]],  # returned data has one dimension
        # dimensions allowed to change size. Must be a set!
        exclude_dims=set((dim,)),
        # vectorize=True,  # not needed since numba takes care of vectorizing
        dask="parallelized",
        # one per output; could also be float or np.dtype("float64")
        output_dtypes=[data.dtype],
    ).rename({"__newdim__": dim})
    interped[dim] = newdim  # need to add this manually

    return interped


xr.testing.assert_allclose(
    expected.transpose(*interped.dims),
    xr_interp(air.chunk({"time": 2, "lon": 2}), "lat", newlat),
)


# This technique is generalizable to any 1D function.
