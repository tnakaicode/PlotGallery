#!/usr/bin/env python
# coding: utf-8


#get_ipython().run_line_magic('matplotlib', 'inline')


import numpy as np
import matplotlib.pyplot as plt
from pymor.basic import *


N = 100

rhs = ExpressionFunction('(x - 0.5)**2 * 1000', 1, ())

d0 = ExpressionFunction('1 - x', 1, ())
d1 = ExpressionFunction('x', 1, ())

f0 = ProjectionParameterFunctional('diffusionl')
f1 = 1.


problem = StationaryProblem(
    domain=LineDomain(),
    rhs=rhs,
    diffusion=LincombFunction([d0, d1], [f0, f1]),
    dirichlet_data=ConstantFunction(value=0, dim_domain=1),
    name='1DProblem'
)


parameter_space = problem.parameters.space(0.1, 1)

discretizer = discretize_stationary_cg
m, data = discretizer(problem, diameter=1 / N)


U = m.solution_space.empty()
for mu in parameter_space.sample_uniformly(10):
    U.append(m.solve(mu))
m.visualize(
    U, title='Solution for diffusionl in [0.1, 1]', separate_plots=True, separate_axes=False)
