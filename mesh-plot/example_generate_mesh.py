"""
================================================================================
Generate meshes from .geo files with Gmsh
================================================================================

Meshes are built with gmsh from `.geo` files then loaded into freshkiss3d.

"""
import os
import numpy as np
import matplotlib.pyplot as plt
import freshkiss3d as fk

################################################################################
#  
# Generate meshes from .geo
#--------------------------
#
#Meshes are generated with gmsh thanks to a ``.geo`` file. The ``.geo`` contains 
#all information gmsh needs to generate a Delaunay triangulation. You can specify
#the number of nodes on boundaries with the `Transfinite` option.
#
#.. note::
#
#    .geo files can be generated with gsmh and are easy to script for simple geometries.
#    Here is an example of a simple canal geometry:    
#
#    .. code-block:: bash
#
#        Lx = 25.0;
#        Ly = 1.0;
#        Point(1) = {0, 0, 0, 1};
#        Point(2) = {Lx, 0, 0, 1};
#        Point(3) = {Lx, Ly, 0, 1};
#        Point(4) = {0, Ly, 0, 1};
#        Line(1) = {1, 2};
#        Line(2) = {2, 3};
#        Line(3) = {3, 4};
#        Line(4) = {4, 1};
#        Line Loop(5) = {3, 4, 1, 2};
#        Plane Surface(0) = {5};
#        Physical Line(1) = {4};
#        Physical Line(2) = {2};
#        Physical Line(3) = {3};
#        Physical Line(4) = {1};
#        Transfinite Line {3, 1} = 50 Using Progression 1;
#        Transfinite Line {4, 2} = 3 Using Progression 1;
#        Physical Surface(0) = {0};

################################################################################
#
#Gmsh can be called via simple commands to generate meshes:

os.system('gmsh -2 inputs/bump0.geo -o inputs/bump0.msh')
os.system('gmsh -2 inputs/bump1.geo -o inputs/bump1.msh')

################################################################################
#
# Construct a TriangularMesh
#------------------------------
#

triangular_mesh_1 = fk.TriangularMesh.from_msh_file('inputs/bump0.msh')
triangular_mesh_2 = fk.TriangularMesh.from_msh_file('inputs/bump1.msh')


################################################################################
#  
# Basic plot
#--------------------
#

TG = triangular_mesh_1.triangulation
x = np.asarray(TG.x)
y = np.asarray(TG.y)
trivtx = np.asarray(TG.trivtx)

TG_r = triangular_mesh_2.triangulation
x_r = np.asarray(TG_r.x)
y_r = np.asarray(TG_r.y)
trivtx_r = np.asarray(TG_r.trivtx)

plt.rcParams["figure.figsize"]=[20,6]
fig = plt.figure()

# Plot 
ax1 = fig.add_subplot(211)
ax1.triplot(x, y, trivtx, color='r')
ax1.set_title("Mesh 1")

# Plot refined mesh
ax2 = fig.add_subplot(212)
ax2.triplot(x_r, y_r, trivtx_r)
ax2.set_title("Mesh 2")

plt.show()

#os.system('rm inputs/bump0.msh')
#os.system('rm inputs/bump1.msh')
