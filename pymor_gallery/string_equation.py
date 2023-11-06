#!/usr/bin/env python
# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

import matplotlib.pyplot as plt
import numpy as np
import scipy.sparse as sps
from typer import Argument, run

from pymor.core.logger import set_log_levels
from pymor.models.iosys import SecondOrderModel
from pymor.reductors.bt import BTReductor
from pymor.reductors.h2 import IRKAReductor
from pymor.reductors.mt import MTReductor
from pymor.reductors.sobt import (
    SOBTfvReductor,
    SOBTpReductor,
    SOBTpvReductor,
    SOBTReductor,
    SOBTvpReductor,
    SOBTvReductor,
)
from pymor.reductors.sor_irka import SORIRKAReductor
from pymordemos.heat import fom_properties, run_mor_method


def main(
        n: int = Argument(101, help='Order of the full second-order model (odd number).'),
        r: int = Argument(5, help='Order of the ROMs.'),
):
    """String equation example."""
    set_log_levels({
        'pymor.algorithms.gram_schmidt.gram_schmidt': 'WARNING',
        'pymor.algorithms.lradi.solve_lyap_lrcf': 'WARNING',
        'pymor.reductors.basic.LTIPGReductor': 'WARNING',
        'pymor.reductors.basic.SOLTIPGReductor': 'WARNING',
    })
    plt.rcParams['axes.grid'] = True

    # Assemble matrices
    assert n % 2 == 1, 'The order has to be an odd integer.'

    n2 = (n + 1) // 2

    d = 10  # damping
    k = 0.01  # stiffness

    M = sps.eye(n, format='csc')
    E = d * sps.eye(n, format='csc')
    K = sps.diags([n * [2 * k * n ** 2],
                   (n - 1) * [-k * n ** 2],
                   (n - 1) * [-k * n ** 2]],
                  [0, -1, 1],
                  format='csc')
    B = np.zeros((n, 1))
    B[n2 - 1, 0] = n
    Cp = np.zeros((1, n))
    Cp[0, n2 - 1] = 1

    # Second-order system
    so_sys = SecondOrderModel.from_matrices(M, E, K, B, Cp)

    # System properties
    w = (1e-4, 1e2)
    fom_properties(so_sys, w)

    # Model order reduction
    run_mor_method(so_sys, w, SOBTpReductor(so_sys), 'SOBTp', r)
    run_mor_method(so_sys, w, SOBTvReductor(so_sys), 'SOBTv', r)
    run_mor_method(so_sys, w, SOBTpvReductor(so_sys), 'SOBTpv', r)
    run_mor_method(so_sys, w, SOBTvpReductor(so_sys), 'SOBTvp', r)
    run_mor_method(so_sys, w, SOBTfvReductor(so_sys), 'SOBTfv', r)
    run_mor_method(so_sys, w, SOBTReductor(so_sys), 'SOBT', r)
    run_mor_method(so_sys, w, SORIRKAReductor(so_sys), 'SOR-IRKA', r,
                   irka_options={'maxit': 10})
    run_mor_method(so_sys, w, BTReductor(so_sys.to_lti()), 'BT', r)
    run_mor_method(so_sys, w, IRKAReductor(so_sys.to_lti()), 'IRKA', r)
    run_mor_method(so_sys, w, MTReductor(so_sys.to_lti()), 'MT', r)


if __name__ == '__main__':
    run(main)
