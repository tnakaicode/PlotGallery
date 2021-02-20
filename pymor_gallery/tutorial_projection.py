from pymor.analyticalproblems.thermalblock import thermal_block_problem
from pymor.discretizers.builtin import discretize_stationary_cg
from pymor.algorithms.pod import pod
from pymor.tools.formatsrc import print_source
from pymor.operators.interface import Operator
from matplotlib import pyplot as plt


# To build the ROM, we will need a reduced space VN of small dimension N. Any subspace of the solution_space of the FOM will do for our purposes here. We choose to build a basic POD space from some random solution snapshots.

p = thermal_block_problem((2, 2))
fom, _ = discretize_stationary_cg(p, diameter=1 / 100)

print_source(fom.solve)
print_source(fom.compute)
print_source(fom._compute_solution)
print_source(Operator.as_range_array)

U = fom.solve([1., 0.1, 0.1, 1.])
fom.visualize(U)

snapshots = fom.solution_space.empty()
for mu in p.parameter_space.sample_randomly(20):
    snapshots.append(fom.solve(mu))
basis, singular_values = pod(snapshots, modes=10)
plt.semilogy(singular_values)

fom.rhs
fom.rhs.source

#U2 = fom.operator.apply_inverse(fom.rhs.as_range_array(mu), mu=[1., 0.1, 0.1, 1.])
mu = fom.parameters.parse([1., 0.1, 0.1, 1.])
U2 = fom.operator.apply_inverse(fom.rhs.as_range_array(mu), mu=mu)
(U - U2).norm()
