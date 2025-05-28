from OCC.Core.BRep import BRep_Tool
from OCC.Core.BRepAdaptor import BRepAdaptor_CompCurve
from OCC.Core.TopoDS import TopoDS_Wire
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopAbs import TopAbs_EDGE
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge,
    BRepBuilderAPI_Sewing,
)
from OCC.Core.BRep import BRep_Builder
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display
import numpy as np


def sample_points_on_wire(wire: TopoDS_Wire, n: int):
    # ワイヤをパラメータ化して等間隔サンプリング
    compcurve = BRepAdaptor_CompCurve(wire)
    first = compcurve.FirstParameter()
    last = compcurve.LastParameter()
    params = np.linspace(first, last, n, endpoint=False)
    points = []
    for u in params:
        pnt = compcurve.Value(u)
        points.append(pnt)
    return points


def minimal_surface_from_wires(wire1: TopoDS_Wire, wire2: TopoDS_Wire, n: int = 100):
    # 2つのワイヤから極小曲面近似（三角形メッシュ）を生成
    pts1 = sample_points_on_wire(wire1, n)
    pts2 = sample_points_on_wire(wire2, n)
    # メッシュ状に三角形面を生成
    edges = []
    for i in range(n):
        i_next = (i + 1) % n
        # 2つの三角形で四角形を埋める
        # 三角形1: pts1[i], pts2[i], pts2[i_next]
        edges.append(
            BRepBuilderAPI_MakeWire(
                BRepBuilderAPI_MakeEdge(pts1[i], pts2[i]).Edge(),
                BRepBuilderAPI_MakeEdge(pts2[i], pts2[i_next]).Edge(),
                BRepBuilderAPI_MakeEdge(pts2[i_next], pts1[i]).Edge(),
            ).Wire()
        )
        # 三角形2: pts1[i], pts2[i_next], pts1[i_next]
        edges.append(
            BRepBuilderAPI_MakeWire(
                BRepBuilderAPI_MakeEdge(pts1[i], pts2[i_next]).Edge(),
                BRepBuilderAPI_MakeEdge(pts2[i_next], pts1[i_next]).Edge(),
                BRepBuilderAPI_MakeEdge(pts1[i_next], pts1[i]).Edge(),
            ).Wire()
        )
    # Sewingでシェル化
    sewing = BRepBuilderAPI_Sewing()
    for w in edges:
        face = BRepBuilderAPI_MakeFace(w)
        sewing.Add(face.Face())
    sewing.Perform()
    shell = sewing.SewedShape()
    return shell


# --- 使用例 ---
if __name__ == "__main__":
    # 例として2つの円ワイヤを生成
    from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
    from OCC.Core.GC import GC_MakeCircle
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire

    n = 100
    # 下円
    ax2_1 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    circle1 = GC_MakeCircle(ax2_1, 1.0).Value()
    edge1 = BRepBuilderAPI_MakeEdge(circle1).Edge()
    wire1 = BRepBuilderAPI_MakeWire(edge1).Wire()
    # 上円（ずらして傾ける例）
    ax2_2 = gp_Ax2(gp_Pnt(0.5, 0.5, 2.0), gp_Dir(0.2, 0.2, 1.0))
    circle2 = GC_MakeCircle(ax2_2, 1.0).Value()
    edge2 = BRepBuilderAPI_MakeEdge(circle2).Edge()
    wire2 = BRepBuilderAPI_MakeWire(edge2).Wire()

    # 極小曲面近似
    shell = minimal_surface_from_wires(wire1, wire2, n=n)

    # 表示
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(wire1, color="red")
    display.DisplayShape(wire2, color="blue")
    display.DisplayShape(shell, update=True)
    display.FitAll()
    start_display()
