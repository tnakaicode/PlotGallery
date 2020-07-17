#!/usr/bin/env python
# coding: utf-8

# # PythonOCC - Example - Topology - Boolean

# Example of the ***BRepAlgoAPI*** functions performing boolean operations: Fuse, Common, Section and Cut.<br>

# In[ ]:


from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Common, BRepAlgoAPI_Section, BRepAlgoAPI_Cut
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_Transform
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeBox, BRepPrimAPI_MakeWedge, BRepPrimAPI_MakeSphere, BRepPrimAPI_MakeTorus
from OCC.Core.gp import gp_Vec, gp_Ax2, gp_Pnt, gp_Dir, gp_Pln, gp_Trsf


# In[ ]:


from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer


# In[ ]:


from ipywidgets import interact, interactive, fixed, interact_manual
import ipywidgets as widgets


# In[ ]:


def translate_topods_from_vector(brep_or_iterable, vec, copy=False):
    '''
    translate a brep over a vector
    @param brep:    the Topo_DS to translate
    @param vec:     the vector defining the translation
    @param copy:    copies to brep if True
    '''
    trns = gp_Trsf()
    trns.SetTranslation(vec)
    brep_trns = BRepBuilderAPI_Transform(brep_or_iterable, trns, copy)
    brep_trns.Build()
    return brep_trns.Shape()


# In[ ]:


def fuse(event=None):
    box1 = BRepPrimAPI_MakeBox(2, 1, 1).Shape()
    box2 = BRepPrimAPI_MakeBox(2, 1, 1).Shape()
    box1 = translate_topods_from_vector(box1, gp_Vec(.5, .5, 0))
    fusedshp = BRepAlgoAPI_Fuse(box1, box2).Shape()
    
    rnd = JupyterRenderer()
    rnd.DisplayShape(fusedshp, render_edges=True)
    rnd.Display()


# In[ ]:


def common(event=None):
    # Create Box
    axe = gp_Ax2(gp_Pnt(10, 10, 10), gp_Dir(1, 2, 1))
    Box = BRepPrimAPI_MakeBox(axe, 60, 80, 100).Shape()
    # Create wedge
    Wedge = BRepPrimAPI_MakeWedge(60., 100., 80., 20.).Shape()
    # Common surface
    CommonSurface = BRepAlgoAPI_Common(Box, Wedge).Shape()

    rnd = JupyterRenderer()
    rnd.DisplayShape(Box, transparency = True, opacity =0.2)
    rnd.DisplayShape(Wedge, transparency = True, opacity =0.2)
    rnd.DisplayShape(CommonSurface, render_edges=True)
    rnd.Display()


# In[ ]:


def slicer(event=None):
    # Param
    Zmin, Zmax, deltaZ = -100, 100, 5
    # Note: the shape can also come from a shape selected from InteractiveViewer
    #if 'display' in dir():
    #    shape = display.GetSelectedShape()
    #else:
    # Create the shape to slice
    shape = BRepPrimAPI_MakeSphere(60.).Shape()
    # Define the direction
    D = gp_Dir(0., 0., 1.)  # the z direction
    # Perform slice
    sections = []
    #init_time = time.time()  # for total time computation
    for z in range(Zmin, Zmax, deltaZ):
        # Create Plane defined by a point and the perpendicular direction
        P = gp_Pnt(0, 0, z)
        Pln = gp_Pln(P, D)
        face = BRepBuilderAPI_MakeFace(Pln).Shape()
        # Computes Shape/Plane intersection
        section_shp = BRepAlgoAPI_Section(shape, face)
        if section_shp.IsDone():
            sections.append(section_shp)
    #total_time = time.time() - init_time
    #print("%.3fs necessary to perform slice." % total_time)
    
    rnd = JupyterRenderer()
    rnd.DisplayShape(shape)
    rnd.Display()
    #for section_ in sections:
    #    rnd.DisplayShape(section_.Shape())


# In[ ]:


def section(event=None):
    torus = BRepPrimAPI_MakeTorus(120, 20).Shape()
    radius = 120.0
    sections = []
    for i in range(-3, 4):
        # Create Sphere
        sphere = BRepPrimAPI_MakeSphere(gp_Pnt(26 * 3 * i, 0, 0), radius).Shape()
        # Computes Torus/Sphere section
        section_shp = BRepAlgoAPI_Section(torus, sphere, False)
        section_shp.ComputePCurveOn1(True)
        section_shp.Approximation(True)
        section_shp.Build()
        sections.append(section_shp)

    rnd = JupyterRenderer()
    rnd.DisplayShape(torus)
    rnd.Display()
    #for section_ in sections:
    #    display.DisplayShape(section_.Shape())


# In[ ]:


def cut(event=None):
    # Create Box
    Box = BRepPrimAPI_MakeBox(200, 60, 60).Shape()
    # Create Sphere
    Sphere = BRepPrimAPI_MakeSphere(gp_Pnt(100, 20, 20), 80).Shape()
    # Cut: the shere is cut 'by' the box
    Cut = BRepAlgoAPI_Cut(Sphere, Box).Shape()
    
    rnd = JupyterRenderer()
    rnd.DisplayShape(Box, transparency = True, opacity =0.2)
    rnd.DisplayShape(Cut, render_edges=True)
    rnd.Display()


# In[ ]:


def f(boolop):
    if boolop == 'fuse':
        fuse()
    elif boolop == 'common':
        common()
    elif boolop == 'slicer':
        slicer()
    elif boolop == 'section':
        section()
    elif boolop == 'cut':
        cut()


# In[ ]:


interact(f, boolop = ['fuse','common', 'slicer', 'section', 'cut']);

