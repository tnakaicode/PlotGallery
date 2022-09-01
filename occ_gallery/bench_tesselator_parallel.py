import os
import os.path
import time

from OCC.Core.Tesselator import ShapeTesselator

from OCC.Extend.TopologyUtils import TopologyExplorer
from OCC.Extend.DataExchange import read_step_file

# TEST 1 : one big STEP file into one single compound
# loads the step file
# load twice, not a copy/paste typo. It's because meshes are stored
# the second time, meshing time is much faster
print("TEST 1 ===")
step_file = os.path.join('assets', 'models', 'RC_Buggy_2_front_suspension.stp')
step_file = "./assets/models/as1-oc-214.stp"
shp = read_step_file(step_file)
#shp2 = read_step_file(step_file)

# tesselate in single thread mode
print("Tesselate in single thread mode")
t_single = ShapeTesselator(shp)
t0 = time.monotonic()
t_single.Compute(parallel=False, mesh_quality=0.5)
t1 = time.monotonic()
delta_single = t1 - t0

print(t_single.ObjGetNormalCount())
print(t_single.GetTriangleIndex(1))
print(t_single.GetVertex(1))

# tesselate in parallel thread mode
print("Tesselate in parallelized mode")
t_multi = ShapeTesselator(shp)
t2 = time.monotonic()
t_multi.Compute(parallel=True, mesh_quality=0.5)
t3 = time.monotonic()
delta_multi = t3 - t2

print("Test 1 Results:")
print("  * single thread runtime: %.2fs" % delta_single)
print("  * multi thread runtime: %.2fs" % delta_multi)
print("  * muti/single=%.2f%%" % (delta_multi / delta_single * 100))

# TEST 2 : other step, with a loop over each subshape
print("TEST 2 ===")
#shp3 = read_step_file(step_file)
#shp4 = read_step_file(step_file)

topo1 = TopologyExplorer(shp)
t4 = time.monotonic()
for solid in topo1.solids():
    o = ShapeTesselator(solid)
    o.Compute(parallel=False, mesh_quality=0.5)
t5 = time.monotonic()
delta_single = t5 - t4

topo2 = TopologyExplorer(shp)
t6 = time.monotonic()
for solid in topo2.solids():
    o = ShapeTesselator(solid)
    o.Compute(parallel=True, mesh_quality=0.5)
t7 = time.monotonic()
delta_multi = t7 - t6

print("Test 2 Results:")
print("  * single thread runtime: %.2fs" % delta_single)
print("  * multi thread runtime: %.2fs" % delta_multi)
print("  * muti/single=%.2f%%" % (delta_multi / delta_single * 100))

from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt
from OCCUtils.Construct import make_polygon, make_face

display, start_display, add_menu, add_functionto_menu = init_display()
print(t_single.ObjGetNormalCount())
print(t_single.ObjGetTriangleCount())
print(t_single.GetTriangleIndex(0))
print(t_single.GetTriangleIndex(1))
print(t_single.GetVertex(1))

num = t_single.ObjGetTriangleCount()
tris = []
for i in range(num):
    idx = i
    #print(t_single.ObjGetInvalidTriangleCount(), t_single.GetTriangleIndex(idx))
    i0, i1, i2 = t_single.GetTriangleIndex(idx)
    p0 = gp_Pnt(*t_single.GetVertex(i0))
    p1 = gp_Pnt(*t_single.GetVertex(i1))
    p2 = gp_Pnt(*t_single.GetVertex(i2))
    rim = make_polygon([p0, p1, p2], True)
    tri = make_face(rim)
    tris.append(tri)

display.DisplayShape(tris)
display.FitAll()
start_display()
