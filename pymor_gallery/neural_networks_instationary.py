#!/usr/bin/env python
# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

import time
import numpy as np
from typer import Argument, run

from pymor.basic import *
from pymor.core.config import config
from pymor.core.exceptions import TorchMissing
from pymor.reductors.neural_network import (NeuralNetworkInstationaryReductor,
                                            NeuralNetworkInstationaryStatefreeOutputReductor)


def main(
    grid_intervals: int = Argument(..., help='Grid interval count.'),
    time_steps: int = Argument(..., help='Number of time steps used for discretization.'),
    training_samples: int = Argument(..., help='Number of samples used for training the neural network.'),
    validation_samples: int = Argument(..., help='Number of samples used for validation during the training phase.'),
):
    """Model oder reduction with neural networks for an instationary problem

    Using the approach by Hesthaven and Ubbiali.
    """
    if not config.HAVE_TORCH:
        raise TorchMissing()

    fom = create_fom(grid_intervals, time_steps)

    parameter_space = fom.parameters.space(1., 2.)

    training_set = parameter_space.sample_uniformly(training_samples)
    validation_set = parameter_space.sample_randomly(validation_samples)

    reductor = NeuralNetworkInstationaryReductor(fom, training_set, validation_set, basis_size=10)
    rom = reductor.reduce(hidden_layers='[30, 30, 30]', restarts=100)

    test_set = parameter_space.sample_randomly(10)

    speedups = []

    print(f'Performing test on set of size {len(test_set)} ...')

    U = fom.solution_space.empty(reserve=len(test_set))
    U_red = fom.solution_space.empty(reserve=len(test_set))

    for mu in test_set:
        tic = time.time()
        U.append(fom.solve(mu))
        time_fom = time.time() - tic

        tic = time.time()
        U_red.append(reductor.reconstruct(rom.solve(mu)))
        time_red = time.time() - tic

        speedups.append(time_fom / time_red)

    absolute_errors = (U - U_red).norm2()
    relative_errors = (U - U_red).norm2() / U.norm2()

    output_reductor = NeuralNetworkInstationaryStatefreeOutputReductor(fom, time_steps+1, training_set,
                                                                       validation_set, validation_loss=1e-5)
    output_rom = output_reductor.reduce(restarts=100)

    outputs = []
    outputs_red = []
    outputs_speedups = []

    print(f'Performing test on set of size {len(test_set)} ...')

    for mu in test_set:
        tic = time.perf_counter()
        outputs.append(fom.compute(output=True, mu=mu)['output'])
        time_fom = time.perf_counter() - tic

        tic = time.perf_counter()
        outputs_red.append(output_rom.compute(output=True, mu=mu)['output'])
        time_red = time.perf_counter() - tic

        outputs_speedups.append(time_fom / time_red)

    outputs = np.squeeze(np.array(outputs))
    outputs_red = np.squeeze(np.array(outputs_red))

    outputs_absolute_errors = np.abs(outputs - outputs_red)
    outputs_relative_errors = np.abs(outputs - outputs_red) / np.abs(outputs)

    print('Results for state approximation:')
    print(f'Average absolute error: {np.average(absolute_errors)}')
    print(f'Average relative error: {np.average(relative_errors)}')
    print(f'Median of speedup: {np.median(speedups)}')

    print()
    print('Results for output approximation:')
    print(f'Average absolute error: {np.average(outputs_absolute_errors)}')
    print(f'Average relative error: {np.average(outputs_relative_errors)}')
    print(f'Median of speedup: {np.median(outputs_speedups)}')


def create_fom(grid_intervals, time_steps):
    problem = burgers_problem()
    f = LincombFunction(
        [ExpressionFunction('1.', 1), ConstantFunction(1., 1)],
        [ProjectionParameterFunctional('exponent'), 0.1])
    problem = problem.with_stationary_part(outputs=[('l2', f)])

    print('Discretize ...')
    fom, _ = discretize_instationary_fv(problem, diameter=1. / grid_intervals, nt=time_steps)

    return fom


if __name__ == '__main__':
    run(main)
