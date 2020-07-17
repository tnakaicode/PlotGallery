#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os

from OCC.Core.gp import gp_Dir
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer
from OCC.Extend.DataExchange import read_step_file, export_shape_to_svg


# In[2]:


my_renderer = JupyterRenderer()


# In[3]:


robot_shp = read_step_file(os.path.join('..', 'assets', 'models', 'KR600_R2830-4.stp'))


# In[5]:


my_renderer.DisplayShapeAsSVG(robot_shp, direction=gp_Dir(1, 1, 0.1),
                              export_hidden_edges=False,
                              line_width=1.5)


# In[ ]:




