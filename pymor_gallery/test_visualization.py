#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from pymor.basic import *
set_defaults({'pymor.discretizers.builtin.gui.jupyter.get_visualizer.backend': 'py3js'})
p = burgers_problem_2d()
d, _ = discretize_instationary_fv(p, num_flux='simplified_engquist_osher', diameter=1/50, nt=100, num_values=10, grid_type=RectGrid)
U = d.solve(2.)
d.visualize(U)

