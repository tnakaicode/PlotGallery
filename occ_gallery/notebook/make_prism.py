#!/usr/bin/env python
# coding: utf-8

# # PythonOCC - Example - Topology - Make Prism

# Example of the ***BRepPrimAPI_MakePrism*** function building linear swept topologies, called prisms.<br>
# In this example, the prism is defined by a bspline edge which is swept along a vector. 
# The result is a face.

# In[1]:


# imports from OCC.Core
from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism


# In[2]:


# imports from Display and Extend
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer


# Creation of the Jupyter Renderer

# In[3]:


my_renderer = JupyterRenderer()


# Generation of the bspline profile using an array of 5 points. The spline is interpolated through these points.

# In[4]:


# the bspline profile
array = TColgp_Array1OfPnt(1, 5)
array.SetValue(1, gp_Pnt(0, 0, 0))
array.SetValue(2, gp_Pnt(1, 2, 0))
array.SetValue(3, gp_Pnt(2, 3, 0))
array.SetValue(4, gp_Pnt(4, 3, 0))
array.SetValue(5, gp_Pnt(5, 5, 0))
bspline = GeomAPI_PointsToBSpline(array).Curve()
profile = BRepBuilderAPI_MakeEdge(bspline).Edge()


# Generation of the linear path.

# In[5]:


# the linear path
starting_point = gp_Pnt(0., 0., 0.)
end_point = gp_Pnt(0., 0., 6.)
vec = gp_Vec(starting_point, end_point)
path = BRepBuilderAPI_MakeEdge(starting_point, end_point).Edge()


# Build the prism model resulting from the bspline extrusion allong the linear path

# In[6]:


# extrusion
prism = BRepPrimAPI_MakePrism(profile, vec).Shape()


# In[7]:


my_renderer.DisplayShape(prism, render_edges=True)


# In[8]:


my_renderer.Display()

