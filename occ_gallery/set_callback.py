#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import sys
sys.path.append('..')

from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeTorus, BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere
from OCC.Core.gp import gp_Vec
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer, NORMAL
from OCC.Core.GProp import GProp_GProps
from OCC.Core.BRepGProp import brepgprop_VolumeProperties

from OCC.Extend.ShapeFactory import translate_shp


# In[ ]:


# create 3 toruses
# be careful to set copy to True or all the shapes will share the same mesh
torus_shp = BRepPrimAPI_MakeTorus(20, 5).Shape()
box_shp = translate_shp(BRepPrimAPI_MakeBox(10, 20, 3).Shape(), gp_Vec(60, 0, 0))
sphere_shp = translate_shp(BRepPrimAPI_MakeSphere(20.).Shape(), gp_Vec(-60, 0, 0))


# In[ ]:


# use the NORMAL.CLIENT_SIDE in order to clearly see faces
# in case the NORMAL.SERVER_SIDE option is used, vertex normals lead to
# a smooth rendering
my_renderer = JupyterRenderer()


# In[ ]:


def a_callback(shp):
    """ called each time a double click is performed
    """
    my_renderer.html.value = "Callback executed !"
my_renderer.register_select_callback(a_callback)


# In[ ]:


my_renderer.DisplayShape(torus_shp, shape_color="blue")
my_renderer.DisplayShape(box_shp, shape_color="red")
my_renderer.DisplayShape(sphere_shp, shape_color="green", update=True)

