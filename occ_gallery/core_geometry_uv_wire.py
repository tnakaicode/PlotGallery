import numpy as np
from math import pi
from OCC.Core.gp import gp_Pnt2d, gp_Circ2d, gp_Ax2d, gp_Dir2d
from OCC.Core.gp import gp_Ax3
from OCC.Core.gp import gp_Pnt
from OCC.Core.GeomAbs import GeomAbs_C0, GeomAbs_C1, GeomAbs_C2
from OCC.Core.GeomAbs import GeomAbs_G1, GeomAbs_G2
from OCC.Core.Geom import Geom_CylindricalSurface
from OCC.Core.Geom import Geom_SphericalSurface
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.Geom2d import Geom2d_TrimmedCurve
from OCC.Core.Geom2dAPI import Geom2dAPI_PointsToBSpline, Geom2dAPI_Interpolate
from OCC.Core.GCE2d import GCE2d_MakeSegment, GCE2d_MakeCircle
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.TColgp import TColgp_Array1OfPnt2d, TColgp_HArray1OfPnt2d
from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.TopoDS import topods
from OCC.Extend.DataExchange import read_step_file, write_step_file
from OCC.Display.SimpleGui import init_display


def uv_polygon2d_to_wire_on_surface(surface, uv_points, close=True):
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
        array.SetValue(i, gp_Pnt2d(u, v))  # Uを周期的に扱う
    harray = TColgp_HArray1OfPnt2d(array)
    curve_builder = Geom2dAPI_Interpolate(harray, True, 0.1E-6)
    curve_builder.Perform()
    spline_2d = curve_builder.Curve()

    # SplineをSurface上のエッジに変換
    edge = BRepBuilderAPI_MakeEdge(spline_2d, surface).Edge()

    # Wireを作成
    wire_maker = BRepBuilderAPI_MakeWire()
    wire_maker.Add(edge)
    return wire_maker.Wire()


def surface_wire_to_uv_wire(face, wire):
    """
    Surface上のWireをUV平面上のWireに変換する関数
    surface: Geom_Surface (例: Geom_CylindricalSurface)
    wire: TopoDS_Wire (Surface上のWire)
    戻り値: TopoDS_Wire (UV平面上のWire)
    """
    # UV平面上のエッジを格納するリスト
    uv_edges = []

    # Wire内のエッジを取得
    explorer = TopExp_Explorer(wire, TopAbs_EDGE)
    while explorer.More():
        edge = topods.Edge(explorer.Current())
        # Surface上のエッジをUV空間の曲線に変換
        curve_2d, first, last = BRep_Tool.CurveOnSurface(edge, face, True)
        trimmed_curve = Geom2d_TrimmedCurve(curve_2d, first, last)
        # UV空間上のエッジを作成
        uv_edge = BRepBuilderAPI_MakeWire(trimmed_curve).Edge()
        uv_edges.append(uv_edge)
        explorer.Next()

    # UV平面上のWireを作成
    wire_maker = BRepBuilderAPI_MakeWire()
    for uv_edge in uv_edges:
        wire_maker.Add(uv_edge)

    return wire_maker.Wire()


display, start_display, add_menu, add_function_to_menu = init_display()

# 円筒面の作成
cylinder = Geom_CylindricalSurface(gp_Ax3(), 5.0)
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
wire = uv_polygon2d_to_wire_on_surface(cylinder, uv_poly, False)

# Surface上のWireをUV平面上のWireに変換
uv_wire = surface_wire_to_uv_wire(face, wire)

# 結果を確認
print("UV Wire:", uv_wire)

display.DisplayShape(uv_wire, update=True)

display.FitAll()
start_display()
