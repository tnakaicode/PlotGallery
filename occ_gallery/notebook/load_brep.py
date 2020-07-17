#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from OCC.Core.BRepTools import breptools_Read
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.BRep import BRep_Builder


# In[ ]:


from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer


# In[ ]:


cylinder_head = TopoDS_Shape()
builder = BRep_Builder()
assert breptools_Read(cylinder_head, '../assets/models/cylinder_head.brep', builder)


# In[ ]:


my_renderer = JupyterRenderer()


# In[ ]:


my_renderer.DisplayShape(cylinder_head, render_edges=True)


# In[ ]:


my_renderer

