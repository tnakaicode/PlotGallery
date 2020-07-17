#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
from random import randint


# In[ ]:


from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer, format_color
from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.DataExchange import read_step_file


# In[ ]:


shp = read_step_file(os.path.join('..', 'assets', 'models',
                                  'RC_Buggy_2_front_suspension.stp'))


# In[ ]:


my_renderer = JupyterRenderer(size=(700, 700))


# In[ ]:


# loop over subshapes so that each subshape is meshed/displayed
t = TopologyExplorer(shp)
for solid in t.solids():
    # random colors, just for fun
    random_color = format_color(randint(0,255), randint(0,255), randint(0,255))
    my_renderer.DisplayShape(solid, shape_color=random_color, render_edges=True)


# In[ ]:


my_renderer.Display()

