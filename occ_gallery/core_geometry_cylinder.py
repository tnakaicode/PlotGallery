import numpy as np
from math import pi
from OCC.Core.gp import gp_Pnt2d
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.Geom import Geom_CylindricalSurface
from OCC.Core.gp import gp_Ax3
from OCC.Core.Geom import Geom_SphericalSurface
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.gp import gp_Pnt
from OCC.Core.GeomAbs import GeomAbs_C0, GeomAbs_C1, GeomAbs_C2
from OCC.Core.GeomAbs import GeomAbs_G1, GeomAbs_G2
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
from OCC.Extend.DataExchange import read_step_file, write_step_file
from OCC.Display.SimpleGui import init_display


def polygon2d_to_wire_on_surface(surface, uv_points, close=True):
    """
    UVパラメータ空間上の2D多角形を、指定したパラメトリックサーフェス上のWireに変換する。
    surface: Geom_Surface (例: Geom_CylindricalSurface, Geom_SphericalSurface, Geom_BSplineSurface)
    uv_points: [(u1, v1), (u2, v2), ...] のリスト
    close: Trueなら閉じる
    戻り値: TopoDS_Wire
    """
    edges = []
    n = len(uv_points)
    for i in range(n if close else n - 1):
        p1 = gp_Pnt2d(*uv_points[i])
        p2 = gp_Pnt2d(*uv_points[(i + 1) % n])
        seg2d = GCE2d_MakeSegment(p1, p2).Value()
        edge = BRepBuilderAPI_MakeEdge(seg2d,
                                       surface,
                                       seg2d.FirstParameter(),
                                       seg2d.LastParameter()).Edge()
        edges.append(edge)
    wire_maker = BRepBuilderAPI_MakeWire()
    for edge in edges:
        wire_maker.Add(edge)
    return wire_maker.Wire()


display, start_display, add_menu, add_function_to_menu = init_display()

# 円筒面
cylinder = Geom_CylindricalSurface(gp_Ax3(), 6.0)
face = BRepBuilderAPI_MakeFace(cylinder.Cylinder(), 0, 2 * pi, -10, 10).Face()

# UV空間上の四角形
uv_poly = [
    (0, 1),
    (pi, 1),
    (pi, 5),
    (pi + pi / 4, 7),
    (pi + pi / 4, 1),
    (2 * pi, 1)
]
wire = polygon2d_to_wire_on_surface(cylinder, uv_poly, False)

face_builder = BRepAlgo_FaceRestrictor()
face_builder.Init(face, True, True)
face_builder.Add(wire)
face_builder.Perform()
face_trimmed = face_builder.Current()

display.DisplayShape(wire, update=True)
display.DisplayShape(face, transparency=0.5)
display.DisplayShape(face_trimmed, color="BLUE1", transparency=0.5)

display.FitAll()
start_display()
