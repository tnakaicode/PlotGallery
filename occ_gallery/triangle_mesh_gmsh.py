#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# standard import 
import os
import sys
import tempfile

# OCC imports
from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer
from OCC.Core.BRepTools import breptools_Write
from OCC.Core.gp import gp_Vec
from OCC.Extend.ShapeFactory import translate_shp
from OCC.Extend.DataExchange import read_step_file, read_stl_file


# In[ ]:


# gmsh binary location
GMSH_BINARY = 'gmsh'

# create a temporary directory to store gmsh files
tmp  =  tempfile.TemporaryDirectory()
TMP_DIR = tmp.name
print("Files will be saved to ", TMP_DIR)


# In[ ]:


ventilator_shp = read_step_file(os.path.join('..', 'assets', 'models', 'Ventilator.stp'))


# In[ ]:


# dump the geometry to a brep file, check it worked
BREP_BASENAME = "ventilator.brep"
BREP_FILENAME = os.path.join(TMP_DIR, BREP_BASENAME)
breptools_Write(ventilator_shp, BREP_FILENAME)
assert os.path.isfile(BREP_FILENAME)

# create the gmesh file
gmsh_file_content = """SetFactory("OpenCASCADE");

Mesh.CharacteristicLengthMin = 1;
Mesh.CharacteristicLengthMax = 5;

a() = ShapeFromFile('%s');
""" % BREP_BASENAME
GEO_FILENAME = os.path.join(TMP_DIR, "ventilator.geo")
gmsh_file = open(GEO_FILENAME, "w")
gmsh_file.write(gmsh_file_content)
gmsh_file.close()
assert os.path.isfile(GEO_FILENAME)

# call gmsh, generate an STL file
STL_FILENAME = os.path.join(TMP_DIR, "ventilator.stl")
os.system("%s %s -2 -o %s -format stl" % (GMSH_BINARY, GEO_FILENAME, STL_FILENAME))
assert os.path.isfile(STL_FILENAME)

# load the stl file
meshed_ventilator_shp = read_stl_file(STL_FILENAME)


# In[ ]:


my_renderer = JupyterRenderer(size=(900, 900))


# In[ ]:


my_renderer.DisplayShape(translate_shp(ventilator_shp, gp_Vec(-100,0,0)), render_edges=True, shape_color="cyan")
my_renderer.DisplayShape(meshed_ventilator_shp, render_edges=True, shape_color="cyan", update=True)

