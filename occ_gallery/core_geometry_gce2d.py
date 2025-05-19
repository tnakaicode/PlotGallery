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
# UV空間上の四角形
uv_poly = [(0, 0), (pi, 5), (0, 5)]
wire1 = polygon2d_to_wire_on_surface(cylinder, uv_poly)
# display.DisplayShape(wire1, update=True)
# display.DisplayShape(BRepBuilderAPI_MakeFace(
#   cylinder.Cylinder(), 0, 2 * pi, -1, 6).Face(), transparency=0.5)


sphere = Geom_SphericalSurface(gp_Ax3(), 10.0)
uv_tri = [(0, 0), (pi / 2, pi / 2), (2.1 * pi, pi / 3)]
wire2 = polygon2d_to_wire_on_surface(sphere, uv_tri)
# display.DisplayShape(wire2, update=True)
# display.DisplayShape(BRepBuilderAPI_MakeFace(
#    sphere.Sphere(), 0, 2 * pi, -pi / 2, pi / 2).Face(), transparency=0.5)

# --- BSplineサーフェスの作成 ---
# 4x4の制御点グリッドを作成
array = TColgp_Array2OfPnt(1, 4, 1, 4)
for u in range(1, 5):
    for v in range(1, 5):
        z = np.sin((u - 1) * np.pi / 3) * np.cos((v - 1) * np.pi / 3) * 2
        array.SetValue(u, v, gp_Pnt((u - 1) * 5, (v - 1) * 5, z))
bspline_surface = GeomAPI_PointsToBSplineSurface(
    array, 3, 8, GeomAbs_G2, 0.0001).Surface()

# サーフェスのパラメータ範囲を取得
u_min, u_max, v_min, v_max = bspline_surface.Bounds()
print(f"u_min: {u_min}, u_max: {u_max}, v_min: {v_min}, v_max: {v_max}")

# --- UV空間上の多角形（例：ひし形） ---
uv_poly = [(0.1, 0.1), (0.2, 0.2), (0.8, 0.5), (0.5, 0.1)]


# --- Wire生成 ---
wire3 = polygon2d_to_wire_on_surface(bspline_surface, uv_poly)
face3 = BRepBuilderAPI_MakeFace(bspline_surface, 1e-6).Face()
display.DisplayShape(wire3, update=True)
display.DisplayShape(face3, transparency=0.5)

api_face = BRepAlgo_FaceRestrictor()
api_face.Init(face3, True, True)
api_face.Add(wire3)
api_face.Perform()
# display.DisplayShape(api_face.Current(), color="BLUE1", transparency=0.5, update=True)

# --- WireでサーフェスをトリムしたFaceを作成 ---
trimmed_face = BRepBuilderAPI_MakeFace(bspline_surface, wire3, True).Face()
display.DisplayShape(trimmed_face, color="GREEN",
                     transparency=0.5, update=True)

write_step_file(trimmed_face, "core_geometry_gce2d_face3_trimmed.step")
write_step_file(face3, "core_geometry_gce2d_face3.step")

display.FitAll()
start_display()
