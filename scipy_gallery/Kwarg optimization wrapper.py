#!/usr/bin/env python
# coding: utf-8

# # Kwargs optimization wrapper
#
# TAGS: Optimization and fitting
#
# ## This ia a method to implement optimization for functions taking keywords instead of a vector (python 3 only since 2 doesn't support multiple dictionnary unpacking simultaneously)
# This was mostly implemented out of the need to optimize a ml algorythm's hyper-parameters, by using factory function and dictionnary packing and unpacking it is possible to achieve this.
#
# ### This is a prototype, some minimal tweaking may be necessary though the functions should be modular enough and have enough safety nets to work as is.
#
#

# ## First function, a random distribution generator
# This first function is a random generator to create an array of X rows(Size parameter), iterating over those row and passing the values to the function can be useful.
# Using a Size of 1 is the recommended way to create a single vector to initiate the optimization process.

from collections import OrderedDict as OD
import numpy as np
from pandas import DataFrame
from random import randint, uniform
from scipy.optimize import minimize
import pandas as pd
from pandas import DataFrame  # to make sure adpt_dstr works


def adpt_distr(boundict, Method: bool = True, Size=1, out='df', hardfloat=True):
    """
    Takes input with bounds, check bounds, if bounds are (float) sample from uniform 0,1
    otherwise if bounds are (bool) sample from randint 0,1 and otherwise sample from randint bound to bound
    return matrix of desired size, first var of size is the number of time and the second is the lenght(num of dims)

    args:
    boundict:
        dictionnary containing the keyword of the function as the key and the associated values are tuple
        the tuple can contain int (minimum_int,Max_int) those values are inclusive
        if you want to return a float set the value as (foat) and if you wan to return a boolean simply set the value as (bool)
    Method:
        if true will create x item for Size per path, otherwise if not will iterate to create each value one by one
    Size: 
        number of random values/rows to be created
    out: 
        return a dataframe unless first letter of input is 'a' then return array
        a dataframe make it possible to have distinct types of values but may not be compatible with minimize
    hardfloat: 
        Force output to be a float, if false the keyword float will return int from 0 to 100
        otherwise if True it will only return a float ranging from 0. to 1.
    """
    vals = dict()
    if not (Method):
        from random import randint, uniform
        if not (isinstance(Size, int)):
            Size = Size[0]
        for sample in range(Size):
            # row creator
            vals = dict()
            for key, vari in boundict.items():
                try:
                    if len(
                            vari
                    ) > 1:  # this means that vari is not bool or float and is the proper size
                        if isinstance(vari[0], float) and isinstance(
                                vari[1], float) and hardfloat:
                            DAT = uniform(low=vari[0], high=vari[1])
                        else:
                            DAT = randint(low=vari[0], high=vari[1])
                except:
                    if vari == bool:
                        DAT = randint(low=0, high=1)
                    elif vari == float:
                        if hardfloat:
                            DAT = uniform(low=0, high=1)
                        else:
                            DAT = randint(low=0, high=100)
                    else:
                        DAT = vari
                vals[key] = DAT
            try:
                try:
                    datafram.append(vals, ignore_index=True)
                except:
                    datafram.append(
                        DataFrame.from_dict(vals, orient='columns'),
                        ignore_index=True)
            except:
                datafram = DataFrame.from_dict(vals, orient='columns')
    else:
        from numpy.random import randint, uniform
        if not (isinstance(Size, int)):
            Size = Size[0]
        for key, vari in boundict.items():
            # take dict of value as input
            try:
                if len(
                        vari
                ) > 1:  # this means that vari is not bool or float and is the proper size
                    if isinstance(vari[0], float) and isinstance(
                            vari[1], float) and hardfloat:
                        DAT = uniform(low=vari[0], high=vari[1], size=Size)
                    else:
                        DAT = randint(low=vari[0], high=vari[1], size=Size)
            except:
                if vari == bool:
                    DAT = randint(low=0, high=1, size=Size)
                elif vari == float:
                    if hardfloat:
                        DAT = uniform(low=0, high=1, size=Size)
                    else:
                        DAT = randint(low=0, high=100, size=Size)
                else:
                    DAT = vari
            vals[key] = DAT
        datafram = DataFrame.from_dict(vals, orient='columns')
    if out[0].lower() == 'a':
        if not (hardfloat):
            out = datafram.as_matrix().astype(int)
        else:
            out = datafram.as_matrix()  # might not be compatible with minimize
        return (out)
    return (datafram)


# ## The core of the method: the dicwrap function
# This is where everything happens, this function is used as a function factory to create a simple function with most things preset, this way minimize can handle the function properly.
#
# There should be enough modularity and safety nets to make this work out of the box. It is possible that something may go wrong ( it has not been tested extensively).
#
# Check the function doc for more details.


def dicwrap(funck,
            boundings,
            lenit: int = 1,
            inpt=None,
            i_as_meth_arg: bool = False,
            factory: bool = True,
            Cmeth: str = "RUN",
            staticD=dict(),
            hardfloat=False,
            inner_bounding=False):
    """take in function and dict and return:
    if factory is True :
        the primed function is returned, this function is the one given to minimize
    if lenit > 0:
        the initiation vector is returned ( if a set of random value is needed to start minimize)
    then:
        the bounds are returned
        and the keywords are also returned, this is useful if you want to combine the vector and
        the names of the values as a dict if you wanted to optimize for than one batch of parameter

    args:
        funck:
            function to optimize
        boundings:
            list or ordered dictionnary, if a list is passed is should be composed of tuples,
            the first level of tuples contains the key and another tuple with a type or the bounds
            i.e.:[('a',(1,100)),('b',(float)),('c',(1,100)),('d',(bool)),('e',(1,100)),('f',(1,100))]
        lenit:
            lenght(row not cols) of the first innit distribution
        inpt:
            main target to process with function ( the main arg of the function)
        i_as_meth_arg:
            if the value of inpt should be only give when the class method is called, then set it to true,
            if inpt should be given to the function or the class __init__ then leave as False
        Cmeth:
            class method to run
        factory:
            act as a factory function to automatically set station and Cmeth
            that way the function will only need the init and args as input, not the station and Cmeth too
        staticD:
            a dictionnary of key word arguments, useful if you want to use previously optimized value and optimize other param
        hardfloat:
            if hardfloat is true, floats will be returned in the initial guess and bounds,
            this is not recomended to use with minimize,
            if floats are needed in the function it is recommended to do a type check and to convert from int to float and divide
        inner_bounding:
            if True, bounds will be enforced inside the generated function and not with scipy,
            otherwise bounds are assumed to be useless or enforced by the optimizer
            """
    if isinstance(boundings, list):
        dicti = OD(boundings)
    elif isinstance(boundings, OD):
        print('good type of input')
    elif isinstance(boundings, dict):
        print(
            "kwargs will be in a random order, use ordered dictionnary instead"
        )
    else:
        print("invalid input for boundings, quitting")
        exit(1)

    dicf = OD()
    args = []
    bounds = []
    initg = []
    if factory and (
            inpt == None
    ):  # set inpt as '' when creating the function to ignore it
        inpt = input(
            'please input the arg that will be executed by the function')
    for ke, va in boundings.items():
        if va == bool:
            dicf[ke] = (0, 1)
        elif va == float:
            if hardfloat:
                dicf[ke] = (0, 1)
            else:
                dicf[ke] = (0, 100)
        elif isinstance(va, tuple):
            dicf[ke] = va
        else:
            try:
                if len(va) > 1:
                    dicf[ke] = tuple(va)
                else:
                    dicf[ke] = va
            except:
                dicf[ke] = va
    if lenit > 0:
        initguess = adpt_distr(
            dicf, out='array', Size=lenit, hardfloat=hardfloat)
    for kk, vv in dicf.items():
        bounds.append(vv)
        args.append(kk)
    if factory:

        def kwargsf(initvs):  # inner funct
            if not (len(initvs) == len(args)):
                if isinstance(initvs,
                              (np.ndarray,
                               np.array)) and len(initvs[0]) == len(args):
                    initvs = initvs[0]
                else:
                    print(initvs)
                    print(len(initvs), len(args))
                    print(initvs.type)
                    print(
                        """initial values provided are not the same lenght as keywords provided,
                    something went wrong, aborting""")
                    exit(1)
            if inner_bounding:
                for i in range(len(bounds)):
                    maxx = max(bounds[i])
                    minn = min(bounds[i])
                    if initvs[i] > maxx:
                        initvs[i] = maxx
                    elif initvs[i] < minn:
                        initvs[i] = minn
            dictos = dict(zip(args, initvs))
            if len(inpt) == 0 or len(
                    inpt) == 1:  # no static input, only values to optimize
                instt = funck(**staticD, **dictos)
            elif i_as_meth_arg:
                # an alternative may be instt=funck(inpt,**staticD,**dictos)
                instt = funck(**staticD, **dictos)
            else:
                instt = funck(inpt, **staticD, **dictos)
            # if an element is present in both dictos and staticD, dictos will overwrite it
            # if you want the element in staticD to never change, place it after dictos
            # check if executing the function return an output
            if not (isinstance(instt, (tuple, int, float, list))
                    or isinstance(instt,
                                  (np.array, np.ndarray, pd.DataFrame))):
                # if no value output is returned then it is assumed that the function is a class instance
                if i_as_meth_arg:
                    outa = getattr(instt, Cmeth)(inpt)
                else:
                    outa = getattr(instt, Cmeth)()
                return (outa)
            else:
                return (instt)

        if lenit > 0:
            if inner_bounding:
                return (kwargsf, initguess, args)
            return (kwargsf, initguess, bounds, args)
        else:
            if inner_bounding:
                return (kwargsf, args)
            return (kwargsf, bounds, args)
    else:
        if inner_bounding:
            return (initguess, args)
        return (initguess, bounds, args)


# ## Example 1: single stage function optimization


# example use

# foo is our function to optimize


def foo(data, first_V=2, second_V=True, third_V=0.23):
    if isinstance(third_v, int):  # force float conversion
        third_V = (float(third_V) / 100)
    pass


# our dinctionnary with our bounds and variable to optimize
kwarg = [('first_V', (0, 23)), ('second_V', (bool)), ('third_V', (float))]

Function, Vector_init, Bounds, Args = dicwrap(
    foo, dicti=kwarg, lenit=1, inpt='')
optimized = minimize(fun=Function, x0=Vector_init, bounds=Bounds)
optimize_kwargs = zip(Args, optimized)


# ## Example 2: Multi-stage class optimization
# If you want to implement optimization in many stages and for a class, this would be the way to do so:


# example use

# foo is our function to optimize


class Cfoo(object):
    def __init__(self, first_V=2, second_V=0.25, third_V=25, fourth_V=True):
        # self.data=data if data is needed at init and not for the method, see the altenate instt suggested and give
        self.first = first_V
        self.second = second_V
        # to showcase convertion for a class, this can be done in the function too
        if isinstance(third_V, int):
            self.third = (float(third_V) / 100)
        else:
            self.third = third_V
        self.fourth = fourth_V

    def EXEC(self, data):
        # do something using the instance variables set by init and some data
        pass


# our dinctionnary with our bounds and variable to optimize
kwarg1 = [('first_V', (0, 23)), ('second_V', (float))]
kwarg2 = [('third_V', (13, 38)), ('fourth_V', (bool))]
optimized_kwargs = OD()  # create empty dict to ensure everything goes well

for dicto in [kwarg1, kwarg2]:
    Function, Vector_init, Bounds, Args = dicwrap(
        foo,
        Cmeth='EXEC',
        dicti=dicto,
        lenit=1,
        inpt=data,
        statiD=optimized_kwargs,
        i_as_meth_arg=True)
    # return the vector of optimized values
    optimized = minimize(fun=Function, x0=Vector_init, bounds=Bounds)
    # combine the values with the corresponding args
    optim_kwargs = zip(Args, optimized)
    optimized_kwargs = {**optimized_kwargs, **
                        optim_kwargs}  # merge the two dicts
