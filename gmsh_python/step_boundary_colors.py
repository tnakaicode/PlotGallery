import gmsh
import os, sys

gmsh.initialize()

path = os.path.dirname(os.path.abspath(__file__))
gmsh.merge(os.path.join(path, 'step_boundary_colors.stp'))

for tag in gmsh.model.getEntities():
    col = gmsh.model.getColor(*tag)
    if col != (0, 0, 255, 0): print('entity', tag, 'color', col)

if '-nopopup' not in sys.argv:
    gmsh.fltk.run()

gmsh.finalize()
