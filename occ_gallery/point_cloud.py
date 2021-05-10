#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os

from OCC.Core.gp import gp_Pnt

from OCC.Display.WebGl.jupyter_renderer import JupyterRenderer


# In[ ]:


def pcd_get_number_of_vertices(pcd_filename):
    """ open the PCD file, read header and get number of vertices.
    Header looks like:
    # .PCD v.5 - Point Cloud Data file format
    VERSION .5
    FIELDS x y z
    SIZE 4 4 4
    TYPE F F F
    COUNT 1 1 1
    WIDTH 397
    HEIGHT 1
    POINTS 397
    DATA ascii
    """
    f = open(pcd_filename, 'r')
    # read 8 lines
    for i in range(8):
        f.readline()
    # the 9th line holds the number of points
    number_of_points = int(f.readline().split()[1])
    f.close()
    return number_of_points


# In[ ]:


pcd_file_name = os.path.join('..', 'assets', 'models', 'bunny.pcd')
# compute number of lines
nbr_of_vertices = pcd_get_number_of_vertices(pcd_file_name)
print("Number of vertices :", nbr_of_vertices)
vertices = []
# fedd it with vertices
fp = open(pcd_file_name, 'r')
# read 11 lines to skip header
for i in range(10):
    fp.readline()
for i in range(nbr_of_vertices):
    line = fp.readline()
    x, y, z = map(float, line.split())
    vertices.append(gp_Pnt(x, y, z))


# In[ ]:


my_renderer = JupyterRenderer()


# In[ ]:


my_renderer.DisplayShape(vertices, update=True)

