#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os.path


# In[ ]:


from IPython.core.display import SVG
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer
from OCC.Extend.DataExchange import read_step_file, export_shape_to_svg


# In[ ]:


shp = read_step_file(os.path.join('..', 'assets', 'models', 'RC_Buggy_2_front_suspension.stp'))


# In[ ]:


my_renderer = JupyterRenderer(size=(800,700))


# In[ ]:


my_renderer.DisplayShape(shp, render_edges=True)


# In[ ]:


my_renderer.Display()

