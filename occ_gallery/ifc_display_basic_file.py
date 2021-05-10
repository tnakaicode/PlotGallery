#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os

from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer, format_color
import ifcopenshell, ifcopenshell.geom


# In[ ]:


ifc_filename = os.path.join('..', 'assets', 'ifc_models', 'AC-11-Smiley-West-04-07-2007.ifc')
assert os.path.isfile(ifc_filename)


# In[ ]:


my_renderer = JupyterRenderer(size=(700, 700))


# In[ ]:


settings = ifcopenshell.geom.settings()
settings.set(settings.USE_PYTHON_OPENCASCADE, True)  # tells ifcopenshell to use pythonocc


# In[ ]:


ifc_file = ifcopenshell.open(ifc_filename)


# In[ ]:


products = ifc_file.by_type("IfcProduct") # traverse all IfcProducts


# In[ ]:


for product in products:
    if product.Representation is not None:  # some IfcProducts don't have any 3d representation
        pdct_shape = ifcopenshell.geom.create_shape(settings, inst=product)
        r,g,b,alpha = pdct_shape.styles[0] # the shape color
        color = format_color(int(abs(r)*255), int(abs(g)*255), int(abs(b)*255))
        # below, the pdct_shape.geometry is a TopoDS_Shape, i.e. can be rendered using
        # any renderer (threejs, x3dom, jupyter, qt5 based etc.)
        my_renderer.DisplayShape(pdct_shape.geometry, shape_color = color, transparency=True, opacity=alpha)


# In[ ]:


my_renderer

