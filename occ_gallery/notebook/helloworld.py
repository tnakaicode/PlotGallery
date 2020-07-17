#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeCylinder
from OCC.Core.gp import gp_Pnt


# In[ ]:


my_renderer = JupyterRenderer()


# In[ ]:


box_shape = BRepPrimAPI_MakeBox(10, 20, 30).Shape()
cylinder_shape = BRepPrimAPI_MakeCylinder(10, 30).Shape()


# In[ ]:


vertices = [gp_Pnt(5, 10, 40), gp_Pnt(10, -4, -10)]
my_renderer.DisplayShape(vertices)


# In[ ]:


my_renderer.DisplayShape(cylinder_shape, render_edges=True, topo_level="Face", shape_color="#abdda4", update=True)

