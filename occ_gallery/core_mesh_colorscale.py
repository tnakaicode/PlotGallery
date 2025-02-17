from OCC.Core.BRep import BRep_Builder, BRep_Tool
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakeWire
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeSphere, BRepPrimAPI_MakePrism
from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
from OCC.Core.Graphic3d import Graphic3d_NOM_DEFAULT
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_FACE
from OCC.Core.TopoDS import TopoDS_Compound, topods
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.gp import gp_Pnt, gp_Vec
from OCC.Core.GeomAPI import GeomAPI_PointsToBSpline
from OCC.Core.TColgp import TColgp_Array1OfPnt

from OCC.Extend.TopologyUtils import TopologyExplorer

import numpy as np

from OCC.Display.OCCViewer import rgb_color
from OCC.Display.SimpleGui import init_display
display, start_display, add_menu, add_function_to_menu = init_display()


def prism():
    # the bspline profile
    array = TColgp_Array1OfPnt(1, 5)
    array.SetValue(1, gp_Pnt(0, 0, 0))
    array.SetValue(2, gp_Pnt(20, 20, 0))
    array.SetValue(3, gp_Pnt(40, 30, 0))
    array.SetValue(4, gp_Pnt(60, 20, 0))
    array.SetValue(5, gp_Pnt(80, 00, 0))
    bspline = GeomAPI_PointsToBSpline(array, 3, 8).Curve()
    profile = BRepBuilderAPI_MakeEdge(bspline).Edge()

    # the linear path
    starting_point = gp_Pnt(0.0, 0.0, 0.0)
    end_point = gp_Pnt(0.0, 0.0, 60.0)
    vec = gp_Vec(starting_point, end_point)
    path = BRepBuilderAPI_MakeEdge(starting_point, end_point).Edge()

    # extrusion
    prism = BRepPrimAPI_MakePrism(profile, vec).Shape()
    return prism


def simple_mesh(shape):
    # Mesh the shape
    BRepMesh_IncrementalMesh(shape, 0.1)
    builder = BRep_Builder()
    comp = TopoDS_Compound()
    builder.MakeCompound(comp)

    bt = BRep_Tool()
    ex = TopExp_Explorer(shape, TopAbs_FACE)
    while ex.More():
        face = topods.Face(ex.Current())
        location = TopLoc_Location()
        facing = bt.Triangulation(face, location)
        tri = facing.Triangles()
        for i in range(1, facing.NbTriangles() + 1):
            wirebuild = BRepBuilderAPI_MakeWire()
            trian = tri.Value(i)
            index1, index2, index3 = trian.Get()
            for j in range(1, 4):
                if j == 1:
                    m = index1
                    n = index2
                elif j == 2:
                    n = index3
                elif j == 3:
                    m = index2
                me = BRepBuilderAPI_MakeEdge(facing.Node(m), facing.Node(n))
                if me.IsDone():
                    wirebuild.Add(me.Edge())
            faace = BRepBuilderAPI_MakeFace(wirebuild.Shape()).Shape()
            builder.Add(comp, faace)
        ex.Next()
    return comp


def get_rgb_color_from_scale(value, bounds=[0, 100]):
    bounds = np.linspace(bounds[0], bounds[1], num=10)
    colors = [(0, 0, 255), (127, 127, 255),
              (0, 255, 255), (0, 255, 127),
              (0, 255, 0), (0, 255, 0),
              (127, 255, 0), (255, 255, 0),
              (255, 127, 0), (255, 0, 0)]
    for i in range(len(bounds) - 1):
        if bounds[i] <= value < bounds[i + 1]:
            ratio = (value - bounds[i]) / (bounds[i + 1] - bounds[i])
            color = [int((colors[i + 1][j] - colors[i][j]) *
                         ratio + colors[i][j]) for j in range(3)]
            rgb = [i / 255 for i in color]
            return tuple(rgb)
    color = colors[-1]
    rgb = [i / 255 for i in color]
    return tuple(rgb)


def minimum_distance(shp1, shp2):
    """
    compute minimum distance between 2 BREP's
    @param shp1:    any TopoDS_*
    @param shp2:    any TopoDS_*

    @return: minimum distance,
             minimum distance points on shp1
             minimum distance points on shp2
    """
    from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape

    bdss = BRepExtrema_DistShapeShape(shp1, shp2)
    bdss.Perform()
    min_dist = bdss.Value()
    min_dist_shp1, min_dist_shp2 = [], []
    for i in range(1, bdss.NbSolution() + 1):
        min_dist_shp1.append(bdss.PointOnShape1(i))
        min_dist_shp2.append(bdss.PointOnShape2(i))
    return min_dist, min_dist_shp1, min_dist_shp2


def colored_mesh_distance(comp, ref):
    distances = []
    for fc in TopologyExplorer(comp).faces():
        dist, _, _ = minimum_distance(ref, fc)
        distances.append(dist)
    # create bounds for the color scale
    bounds = [min(distances), max(distances)]
    display.default_drawer.SetFaceBoundaryDraw(False)
    for fc, dist in zip(TopologyExplorer(comp).faces(), distances):
        color = get_rgb_color_from_scale(dist, bounds=bounds)
        display.DisplayShape(fc,
                             color=rgb_color(*color),
                             material=Graphic3d_NOM_DEFAULT)
    display.FitAll()


if __name__ == "__main__":
    # Create shape
    shape = prism()
    # Create a compound of faces from the shape meshed
    comp = simple_mesh(shape)
    # Create reference shape
    point = gp_Pnt(40, 15, 30)
    pt_sphere = BRepPrimAPI_MakeSphere(point, 0.5).Shape()
    display.DisplayShape(pt_sphere)
    # color a face according to its distance to the ref
    colored_mesh_distance(comp, pt_sphere)
    start_display()
