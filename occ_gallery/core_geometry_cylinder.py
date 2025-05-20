import numpy as np
from math import pi
from OCC.Core.gp import gp_Pnt2d, gp_Circ2d, gp_Ax2d, gp_Dir2d
from OCC.Core.GCE2d import GCE2d_MakeSegment, GCE2d_MakeCircle
from OCC.Core.TColgp import TColgp_Array1OfPnt2d
from OCC.Core.Geom2dAPI import Geom2dAPI_PointsToBSpline
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


def uv_circle_to_wire_on_surface(surface, center_uv, radius, num_segments=100):
    """
    UV空間上の円を指定したパラメトリックサーフェス上のWireに変換する。
    surface: Geom_Surface (例: Geom_CylindricalSurface)
    center_uv: (u, v) 円の中心のUV座標
    radius: 円の半径
    num_segments: 円を近似するセグメント数（デフォルト: 100）
    戻り値: TopoDS_Wire
    """
    # UV空間上の円を作成
    center = gp_Pnt2d(center_uv[0] % (2 * pi), center_uv[1])  # Uを周期的に扱う
    axis = gp_Ax2d(center, gp_Dir2d(1, 0))  # 円の中心と法線ベクトル
    circle = gp_Circ2d(axis, radius)
    circle_edge = GCE2d_MakeCircle(circle).Value()

    # 円をSurface上のエッジに変換
    edge = BRepBuilderAPI_MakeEdge(circle_edge, surface).Edge()

    # Wireを作成
    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(edge)
    return wire_maker.Wire()


def uv_spline_to_wire_on_surface(surface, uv_points):
    """
    UV空間上のSplineを指定したパラメトリックサーフェス上のWireに変換する。
    surface: Geom_Surface (例: Geom_CylindricalSurface)
    uv_points: [(u1, v1), (u2, v2), ...] のリスト
    戻り値: TopoDS_Wire
    """
    # UV空間上の点列をSplineに変換
    array = TColgp_Array1OfPnt2d(1, len(uv_points))
    for i, (u, v) in enumerate(uv_points, start=1):
        array.SetValue(i, gp_Pnt2d(u % (2 * pi), v))  # Uを周期的に扱う
    spline_2d = Geom2dAPI_PointsToBSpline(array).Curve()

    # SplineをSurface上のエッジに変換
    edge = BRepBuilderAPI_MakeEdge(spline_2d, surface).Edge()

    # Wireを作成
    wire_maker = BRepBuilderAPI_MakeWire()
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
    (2 * pi, 1),
]
wire = polygon2d_to_wire_on_surface(cylinder, uv_poly, False)
print("Wireの開閉:", wire.Closed())
print("Wireの向き:", wire.Orientation())

# UV空間上の円をSurface上のWireに変換
center_uv = (pi, 0)  # UV空間上の円の中心
radius = 2          # UV空間上の円の半径
wire_circle = uv_circle_to_wire_on_surface(cylinder, center_uv, radius)

# UV空間上のSplineをSurface上のWireに変換
uv_points = [
    (0, 1),
    (pi / 2, 2),
    (pi, 3),
    (3 * pi / 2, 2),
    (2 * pi, 1)
]
wire_spline = uv_spline_to_wire_on_surface(cylinder, uv_points)

face_builder = BRepAlgo_FaceRestrictor()
face_builder.Init(face, False, True)
face_builder.Add(wire_circle)
face_builder.Perform()
face_trimmed = face_builder.Current()

face_builder = BRepBuilderAPI_MakeFace(face)
face_builder.Add(wire_circle.Reversed())
face_trimmed = face_builder.Face()

# write_step_file(face_trimmed, "core_geometry_cylinder_trimmed.step")

display.DisplayShape(wire, update=True)
display.DisplayShape(wire_circle, update=True)
display.DisplayShape(wire_spline, update=True)
display.DisplayShape(face, transparency=0.5)
display.DisplayShape(face_trimmed, color="BLUE1", transparency=0.5)

display.FitAll()
start_display()
