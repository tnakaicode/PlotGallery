import numpy as np
from math import pi
from OCC.Core.gp import gp_Pnt2d, gp_Ax3, gp_Pnt
from OCC.Core.GCE2d import GCE2d_MakeSegment
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, BRepBuilderAPI_MakeFace
from OCC.Core.Geom import Geom_BSplineSurface
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAbs import GeomAbs_G2
from OCC.Core.BRepAlgo import BRepAlgo_FaceRestrictor
from OCC.Core.ShapeAnalysis import ShapeAnalysis_Wire
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_WIRE
from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Extend.DataExchange import read_step_file, write_step_file
from OCC.Display.SimpleGui import init_display


def polygon2d_to_wire_on_surface(surface, uv_points, close=True):
    edges = []
    n = len(uv_points)
    for i in range(n if close else n - 1):
        p1 = gp_Pnt2d(*uv_points[i])
        p2 = gp_Pnt2d(*uv_points[(i + 1) % n])
        seg2d = GCE2d_MakeSegment(p1, p2).Value()
        edge = BRepBuilderAPI_MakeEdge(
            seg2d, surface, seg2d.FirstParameter(), seg2d.LastParameter()).Edge()
        edges.append(edge)
    wire_maker = BRepBuilderAPI_MakeWire()
    for edge in edges:
        wire_maker.Add(edge)
    return wire_maker.Wire()


def is_wire_closed_and_oriented(wire=TopoDS_Wire()):
    saw = ShapeAnalysis_Wire()
    wire = wire.Oriented(1)
    saw.Load(wire)
    api = saw.WireData().WireAPIMake()
    print("Wireの向き:", api.Orientation())
    print("Wireの向き付け可能性:", api.Orientable())
    print("Wireの閉じ:", api.Closed())


def extract_outer_and_inner_wires(face):
    outer_wire = None
    inner_wires = []
    exp = TopExp_Explorer(face, TopAbs_WIRE)
    while exp.More():
        wire = exp.Current()
        # ワイヤの向きを確認
        saw = ShapeAnalysis_Wire()
        saw.Load(wire)
        if saw.Orientation():  # 外環と判定
            outer_wire = wire
        else:  # 内環と判定
            inner_wires.append(wire)
        exp.Next()
    return outer_wire, inner_wires


display, start_display, *_ = init_display()

# --- サーフェス作成 ---
array = TColgp_Array2OfPnt(1, 10, 1, 10)
for u in range(1, 11):
    for v in range(1, 11):
        z = np.sin((u - 1) * np.pi / 3) * np.cos((v - 1) * np.pi / 3) * 2
        array.SetValue(u, v, gp_Pnt((u - 1) * 10, (v - 1) * 10, z))
bspline_surface = GeomAPI_PointsToBSplineSurface(
    array, 3, 8, GeomAbs_G2, 1e-6).Surface()

# サーフェスのパラメータ範囲を取得
u_min, u_max, v_min, v_max = bspline_surface.Bounds()
print(f"u_min: {u_min}, u_max: {u_max}, v_min: {v_min}, v_max: {v_max}")

# --- 外環ワイヤ ---
outer = [(0.1, 0.1), (0.9, 0.1), (0.9, 0.9), (0.1, 0.9)]
wire_outer = polygon2d_to_wire_on_surface(bspline_surface, outer)

# --- 内環ワイヤ（穴1）---
hole1 = [(0.1, 0.1), (0.6, 0.3), (0.4, 0.5), (0.3, 0.7)]
wire_hole1 = polygon2d_to_wire_on_surface(bspline_surface, hole1)

# --- 内環ワイヤ（穴2：hole1と一部重なる）---
hole2 = [(0.4, 0.4), (0.6, 0.5), (0.6, 0.6), (0.4, 0.6)]
wire_hole2 = polygon2d_to_wire_on_surface(bspline_surface, hole2)

# --- Face作成（外環＋穴1）---
face = BRepBuilderAPI_MakeFace(bspline_surface, 1e-6).Face()

is_wire_closed_and_oriented(wire_hole1)
is_wire_closed_and_oriented(wire_hole1.Reversed())
face_builder = BRepBuilderAPI_MakeFace(bspline_surface, 1e-6)
face_builder.Add(wire_hole1.Reversed())
face_with_hole = face_builder.Face()

# fr = BRepAlgo_FaceRestrictor()
# fr.Init(face, True, True)
# fr.Add(wire_hole1)
# fr.Perform()
# face_with_hole = fr.Current()

# --- FaceRestrictorでさらにhole2を追加 ---
fr1 = BRepAlgo_FaceRestrictor()
fr1.Init(face_with_hole, True, True)
fr1.Add(wire_hole2.Reversed())
fr1.Perform()
trimmed1 = fr1.Current()
write_step_file(trimmed1, "core_geometry_face_trimmed1.step")

fr2 = BRepBuilderAPI_MakeFace(face_with_hole, wire_hole2)
fr2.Add(wire_hole2.Reversed())
trimmed2 = fr2.Face()
write_step_file(trimmed2, "core_geometry_face_trimmed2.step")

fr3 = BRepBuilderAPI_MakeFace(face_with_hole)
fr3.Add(wire_hole2)
trimmed3 = fr3.Face()
write_step_file(trimmed3, "core_geometry_face_trimmed3.step")

# display.DisplayShape(face, color="RED", transparency=0.5, update=True)
display.DisplayShape(face_with_hole, transparency=0.5, update=True)
# display.DisplayShape(wire_outer, color="RED", update=True)
# display.DisplayShape(wire_hole1, color="BLUE1", update=True)
# display.DisplayShape(wire_hole2, color="GREEN", update=True)
# display.DisplayShape(trimmed1, color="YELLOW", transparency=0.2, update=True)
display.DisplayShape(trimmed2, color="BLUE1", transparency=0.2, update=True)
# display.DisplayShape(trimmed3, color="GREEN", transparency=0.2, update=True)

print("FaceRestrictorでhole1とhole2が重なった部分の処理を確認してください。")
print("外環はCCW（反時計回り）、内環はCW（時計回り）")

display.FitAll()
start_display()
