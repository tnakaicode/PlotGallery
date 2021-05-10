#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys

from OCC.Display.WebGl import threejs_renderer
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus
from OCC.Core.gp import gp_Vec
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer, NORMAL
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox

sys.path.append('..')
from OCC.Extend.ShapeFactory import translate_shp


# In[ ]:


# create 3 toruses
# be careful to set copy to True or all the shapes will share the same mesh
torus_shp1 = BRepPrimAPI_MakeTorus(20, 5).Shape()
torus_shp2 = translate_shp(torus_shp1, gp_Vec(60, 0, 0), copy=True)
torus_shp3 = translate_shp(torus_shp1, gp_Vec(-60, 0, 0), copy=True)


# In[ ]:


# use the NORMAL.CLIENT_SIDE in order to clearly see faces
# in case the NORMAL.SERVER_SIDE option is used, vertex normals lead to
# a smooth rendering
my_renderer = JupyterRenderer(compute_normals_mode=NORMAL.CLIENT_SIDE)


# In[ ]:


my_renderer.DisplayShape(torus_shp1, shape_color="blue", topo_level="Face", quality=1.)  # default quality
my_renderer.DisplayShape(torus_shp2, shape_color="red", quality=4)  # lower quality
my_renderer.DisplayShape(torus_shp3, shape_color="green", quality=0.5)  # better quality


# In[ ]:


my_renderer

