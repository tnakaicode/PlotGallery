Cookbook : scikit-fdiff by examples
===================================

Benchmarking:
-------------

All the examples have been run on three different hardware.

- Hardware 1: Laptop, Intel(R) Core(TM) m3-6Y30 CPU @ 0.90GHz **4 cpu**
- Hardware 2: Desktop, Intel(R) Core(TM) i7-3770 CPU @ 3.40GHz **8 cpu**
- Hardware 3: Workstation, Intel(R) Xeon(R) CPU E5-2630 v3 @ 2.40GHz **32 cpu**

They have been obtained a simple gnu `time` command, and take into account
the full script, including model compilation and plotting. The former can
add non-neglectible overhead, especially in 2D cases or complex models.

+-------------------+-----------+--------------+-------------+--------------+
|                   | Mesh size |  Hardware 1  | Hardware 2  |  Hardware 3  |
+===================+===========+==============+=============+==============+
| 1D KDV            | 1000      | 35 sec       | 18 sec      | 17 sec       |
+-------------------+-----------+--------------+-------------+--------------+
| 1D Dam break      | 1000      | 14 sec       | 7 sec       | 7 sec        |
+-------------------+-----------+--------------+-------------+--------------+
| 1D Steady Lake    | 500       | 34 sec       | 18 sec      | 17 sec       |
+-------------------+-----------+--------------+-------------+--------------+
| 2D Acoustic waves | 256 x 256 | 5 min 38 sec | 3 min 9 sec | 2 min 31 sec |
+-------------------+-----------+--------------+-------------+--------------+
| 2D Dam break      | 128 x 128 | 1 min 40 sec | 1 min 8     | 55 sec       |
+-------------------+-----------+--------------+-------------+--------------+

The cpu frequency has a huge impact on the performance on every cases, but the
number of core has more impact on 2D cases, where the system is big enough to
take advantage of the parallelisation.

In these cases, most of the time is spent in the linear system solver. These
operation is hard to parallelize, explaining a bad scaling factor.

However, using explicit solver with the numba backend (or a custom cuda
backend) will efficiently scale up for non-stiff applications.

.. Todo: real benchmarking + scaling factor on one of the hardware.

Gallery
-------
