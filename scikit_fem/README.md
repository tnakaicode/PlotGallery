---
title: Scikit-fem
---

```bash
git clone https://github.com/kinnala/scikit-fem.git
```

## Peformace Test

|     | Degrees-of-freedom | Assembly (s) | Linear solve (s) |
| --- | ------------------ | ------------ | ---------------- |
| 6   | 64                 | 0.00379      | 0.00163          |
| 7   | 125                | 0.00316      | 0.00088          |
| 8   | 216                | 0.00338      | 0.00098          |
| 9   | 512                | 0.00559      | 0.00224          |
| 10  | 1000               | 0.01190      | 0.00252          |
| 11  | 1728               | 0.02005      | 0.00499          |
| 12  | 4096               | 0.05591      | 0.03110          |
| 13  | 8000               | 0.12090      | 0.10694          |
| 14  | 15625              | 0.29180      | 0.55094          |
| 15  | 32768              | 0.59837      | 3.93674          |
| 16  | 64000              | 1.20961      | 20.77431         |
| 17  | 125000             | 2.83781      | nan              |
| 18  | 262144             | 5.53232      | nan              |
| 19  | 512000             | 10.89911     | nan              |
| 20  | 1030301            | 21.68128     | nan              |

## Gallery

Poisson equation
 Example 1: Poisson equation with unit load
 Example 7: Discontinuous Galerkin method
 Example 12: Postprocessing
 Example 13: Laplace with mixed boundary conditions
 Example 14: Laplace with inhomogeneous boundary conditions
 Example 15: One-dimensional Poisson equation
 Example 9: Three-dimensional Poisson equation (need install pyamg/pyamgcl/vedo)
 Example 22: Adaptive Poisson equation
 Example 37: Mixed Poisson equation
 Example 38: Point source
*Example 40: Hybridizable discontinuous Galerkin method
 Example 41: Mixed meshes

Solid mechanics
 Example 2: Kirchhoff plate bending problem
 Example 3: Linear elastic eigenvalue problem
 Example 4: Linearized contact problem
 Example 8: Argyris basis functions
 Example 11: Three-dimensional linear elasticity
 Example 21: Structural vibration
 Example 34: Euler-Bernoulli beam
 Example 36: Nearly incompressible hyperelasticity
 Example 43: Hyperelasticity (need install vedo)

Fluid mechanics
 Example 18: Stokes equations
 Example 20: Creeping flow via stream-function
 Example 24: Stokes flow with inhomogeneous boundary conditions
 Example 29: Linear hydrodynamic stability
 Example 30: Krylov-Uzawa method for the Stokes equation
 Example 32: Block diagonally preconditioned Stokes solver (need install pyamg/pyamgcl)
 Example 42: Periodic meshes

Heat transfer
 Example 17: Insulated wire
 Example 19: Heat equation
 Example 25: Forced convection
 Example 26: Restricting problem to a subdomain
 Example 28: Conjugate heat transfer
 Example 39: One-dimensional heat equation

Miscellaneous
 Example 10: Nonlinear minimal surface problem
 Example 16: Legendre’s equation
 Example 31: Curved elements
 Example 33: H(curl) conforming model problem
*Example 35: Characteristic impedance and velocity factor (E/H Cal)
 Example 44: Wave equation
*Example 46: Waveguide Cutoff Analysis
 Example 47: Projection between two meshes using supermesh
 Example 48: Solve :math:`\Delta^2 u = 1` using HHJ element.
 Example 47: Projection between two meshes using supermesh (need install shapely)

## Run

|                  |             |                           |                                                                            |
| ---------------- | ----------- | ------------------------- | -------------------------------------------------------------------------- |
| Poisson equation | Example 1:  | ![pic](ex01_solution.png) | Poisson equation with unit load                                            |
|                  | Example 7:  | ![pic](ex07_solution.png) | Discontinuous Galerkin method                                              |
|                  | Example 12: | ![pic](ex12_solution.png) | Postprocessing                                                             |
|                  | Example 13: | ![pic](ex13_solution.png) | Laplace with mixed boundary conditions                                     |
|                  | Example 14: | ![pic](ex14_solution.png) | Laplace with inhomogeneous boundary conditions                             |
|                  | Example 15: | ![pic](ex15_solution.png) | One-dimensional Poisson equation                                           |
|                  | Example 9:  | ![pic](ex09_solution.png) | Three-dimensional Poisson equation (need install pyamg/pyamgcl/vedo)       |
|                  | Example 22: | ![pic](ex22_solution.png) | Adaptive Poisson equation                                                  |
|                  | Example 37: | ![pic](ex37_solution.png) | Mixed Poisson equation                                                     |
|                  | Example 38: | ![pic](ex38_solution.png) | Point source                                                               |
|                  | Example 40: | ![pic](ex40_solution.png) | Hybridizable discontinuous Galerkin method                                 |
|                  | Example 41: | ![pic](ex41_solution.png) | Mixed meshes                                                               |
| Solid mechanics  | Example 2:  | ![pic](ex02_solution.png) | Kirchhoff plate bending problem                                            |
|                  | Example 3:  | ![pic](ex03_solution.png) | Linear elastic eigenvalue problem                                          |
|                  | Example 4:  | ![pic](ex04_solution.png) | Linearized contact problem                                                 |
|                  | Example 8:  | ![pic](ex08_solution.png) | Argyris basis functions                                                    |
|                  | Example 11: | ![pic](ex11_solution.png) | Three-dimensional linear elasticity                                        |
|                  | Example 21: | ![pic](ex21_solution.png) | Structural vibration                                                       |
|                  | Example 34: | ![pic](ex34_solution.png) | Euler-Bernoulli beam                                                       |
|                  | Example 36: | ![pic](ex36_solution.png) | Nearly incompressible hyperelasticity                                      |
|                  | Example 43: | ![pic](ex43_solution.png) | Hyperelasticity (need install vedo)                                        |
| Fluid mechanics  | Example 18: | ![pic](ex18_pressure.png) | Stokes equations                                                           |
|                  | Example 20: | ![pic](ex20_solution.png) | Creeping flow via stream-function                                          |
|                  | Example 24: | ![pic](ex24_solution.png) | Stokes flow with inhomogeneous boundary conditions                         |
|                  | Example 29: | ![pic](ex29_solution.png) | Linear hydrodynamic stability                                              |
|                  | Example 30: | ![pic](ex30_solution.png) | Krylov-Uzawa method for the Stokes equation                                |
|                  | Example 32: | ![pic](ex32_solution.png) | Block diagonally preconditioned Stokes solver (need install pyamg/pyamgcl) |
|                  | Example 42: | ![pic](ex42_solution.png) | Periodic meshes                                                            |
| Heat transfer    | Example 17: | ![pic](ex17_solution.png) | Insulated wire                                                             |
|                  | Example 19: | ![pic](ex19.gif)          | Heat equation                                                              |
|                  | Example 25: | ![pic](ex25_solution.png) | Forced convection                                                          |
|                  | Example 26: | ![pic](ex26_solution.png) | Restricting problem to a subdomain                                         |
|                  | Example 28: | ![pic](ex28.png)          | Conjugate heat transfer                                                    |
|                  | Example 39: | ![pic](ex39.gif)          | One-dimensional heat equation                                              |
| Miscellaneous    | Example 10: | ![pic](ex10_solution.png) | Nonlinear minimal surface problem                                          |
|                  | Example 16: | ![pic](ex16_solution.png) | Legendre’s equation                                                        |
|                  | Example 31: | ![pic](ex31_solution.png) | Curved elements                                                            |
|                  | Example 33: | ![pic](ex33_solution.png) | H(curl) conforming model problem                                           |
|                  | Example 35: | ![pic](ex35_solution.png) | Characteristic impedance and velocity factor (E/H Cal)                     |
|                  | Example 44: | ![pic](ex44_solution.png) | Wave equation                                                              |
|                  | Example 46: | ![pic](ex46_solution.png) | Waveguide Cutoff Analysis                                                  |
|                  | Example 47: | ![pic](ex47_solution.png) | Projection between two meshes using supermesh                              |
|                  | Example 48: | ![pic](ex48_solution.png) | Solve :math:`\Delta^2 u = 1` using HHJ element.                            |
|                  | Example 47: | ![pic](ex47_solution.png) | Projection between two meshes using supermesh (need install shapely)       |
