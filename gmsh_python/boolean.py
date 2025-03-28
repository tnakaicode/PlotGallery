# This reimplements gmsh/examples/boolean/boolean.geo in Python.

import gmsh
import sys

gmsh.initialize(sys.argv)

gmsh.model.add("boolean")

# from http://en.wikipedia.org/wiki/Constructive_solid_geometry

gmsh.option.setNumber("Mesh.Algorithm", 6)
gmsh.option.setNumber("Mesh.MeshSizeMin", 0.4)
gmsh.option.setNumber("Mesh.MeshSizeMax", 0.4)

R = 1.4
Rs = R * .7
Rt = R * 1.25

gmsh.model.occ.addBox(-R, -R, -R, 2 * R, 2 * R, 2 * R, 1)
gmsh.model.occ.addSphere(0, 0, 0, Rt, 2)
gmsh.model.occ.intersect([(3, 1)], [(3, 2)], 3)
gmsh.model.occ.addCylinder(-2 * R, 0, 0, 4 * R, 0, 0, Rs, 4)
gmsh.model.occ.addCylinder(0, -2 * R, 0, 0, 4 * R, 0, Rs, 5)
gmsh.model.occ.addCylinder(0, 0, -2 * R, 0, 0, 4 * R, Rs, 6)
gmsh.model.occ.fuse([(3, 4), (3, 5)], [(3, 6)], 7)
gmsh.model.occ.cut([(3, 3)], [(3, 7)], 8)

gmsh.model.occ.synchronize()

gmsh.model.mesh.generate(3)
#gmsh.model.mesh.refine()
#gmsh.model.mesh.setOrder(2)
#gmsh.model.mesh.partition(4)

gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.write("boolean.msh")

gmsh.finalize()
