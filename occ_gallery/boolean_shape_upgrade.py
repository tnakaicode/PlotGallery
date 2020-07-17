#!/usr/bin/env python
# coding: utf-8

# # PythonOCC - Example - Topology - Upgrade - UnifySameDomain

# Example of the ***ShapeUpgrade_UnifySameDomain*** tool unifying all possible faces and edges of a shape which lies on the same geometry.<br><br>
# Faces/edges are considered as 'same-domain' if the neighboring faces/edges lie on coincident surfaces/curves. Such faces/edges can be unified into one face/edge. This tool takes an input shape and returns a new one. All modifications of the initial shape are recorded during the operation.<br>

# In[ ]:


from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox
from OCC.Core.gp import gp_Vec, gp_Trsf
from OCC.Core.ShapeUpgrade import ShapeUpgrade_UnifySameDomain


# In[ ]:


from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer


# Fuse two boxes.

# In[ ]:


box1 = BRepPrimAPI_MakeBox(10., 20., 30.).Shape()
box2 = BRepPrimAPI_MakeBox(20., 1., 30.).Shape()
fused_shp = BRepAlgoAPI_Fuse(box1, box2).Shape()


# Display the union of two boxes. Edges appears from the input of the initial boxes' boundaries.

# In[ ]:


rnd = JupyterRenderer()
rnd.DisplayShape(fused_shp, render_edges=True, update=True)


# Apply the upgrading tool to unify the faces and edges.

# In[ ]:


shapeUpgrade = ShapeUpgrade_UnifySameDomain(fused_shp, False, True, False)
shapeUpgrade.Build()
fused_shp_upgrade = shapeUpgrade.Shape()


# In[ ]:


rnd_upgrade = JupyterRenderer()
rnd_upgrade.DisplayShape(fused_shp_upgrade, render_edges=True, update=True)

