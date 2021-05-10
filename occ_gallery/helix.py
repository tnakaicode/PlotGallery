#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from math import pi

from OCC.Core.gp import gp_Pnt2d, gp_XOY, gp_Lin2d, gp_Ax3, gp_Dir2d
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.Geom import Geom_CylindricalSurface
from OCC.Core.GCE2d import GCE2d_MakeSegment


# In[ ]:


from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer


# In[ ]:


# Build an helix
aCylinder = Geom_CylindricalSurface(gp_Ax3(gp_XOY()), 6.0)
aLine2d = gp_Lin2d (gp_Pnt2d(0.0, 0.0), gp_Dir2d(1.0, 1.0))
aSegment = GCE2d_MakeSegment(aLine2d, 0.0, pi * 2.0)

helix_edge = BRepBuilderAPI_MakeEdge(aSegment.Value(), aCylinder, 0.0, 6.0 * pi).Edge()


# In[ ]:


my_renderer = JupyterRenderer()


# In[ ]:


my_renderer.DisplayShape(helix_edge, update=True)

