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


def minimal_surface_from_wires_minimal_like(
    wire1: TopoDS_Wire, wire2: TopoDS_Wire, n: int = 100, m: int = 30, shrink_ratio=0.5
):
    # 2つのワイヤから極小曲面近似（三角形メッシュ）を生成
    pts1 = sample_points_on_wire(wire1, n)
    pts2 = sample_points_on_wire(wire2, n)
    # 法線方向（大雑把にワイヤ中心線方向）
    center1 = np.mean([[p.X(), p.Y(), p.Z()] for p in pts1], axis=0)
    center2 = np.mean([[p.X(), p.Y(), p.Z()] for p in pts2], axis=0)
    axis = center2 - center1
    axis = axis / np.linalg.norm(axis)
    # 曲面点リスト
    grid = []
    for k in range(m):
        t = k / (m - 1)
        # cosh型で中央を引き込む補間
        s = (np.cosh((t - 0.5) * 2) - np.cosh(1)) / (np.cosh(0) - np.cosh(1))
        ring = []
        for i in range(n):
            p1 = np.array([pts1[i].X(), pts1[i].Y(), pts1[i].Z()])
            p2 = np.array([pts2[i].X(), pts2[i].Y(), pts2[i].Z()])
            p = (
                (1 - t) * p1
                + t * p2
                + axis * s * shrink_ratio * np.linalg.norm(p2 - p1) * 0.5
            )
            ring.append(gp_Pnt(*p))
        grid.append(ring)
    # メッシュ状に三角形面を生成
    edges = []
    for k in range(m - 1):
        for i in range(n):
            i_next = (i + 1) % n
            p1 = grid[k][i]
            p2 = grid[k + 1][i]
            p3 = grid[k + 1][i_next]
            p4 = grid[k][i_next]
            edges.append(
                BRepBuilderAPI_MakeWire(
                    BRepBuilderAPI_MakeEdge(p1, p2).Edge(),
                    BRepBuilderAPI_MakeEdge(p2, p3).Edge(),
                    BRepBuilderAPI_MakeEdge(p3, p1).Edge(),
                ).Wire()
            )
            edges.append(
                BRepBuilderAPI_MakeWire(
                    BRepBuilderAPI_MakeEdge(p1, p3).Edge(),
                    BRepBuilderAPI_MakeEdge(p3, p4).Edge(),
                    BRepBuilderAPI_MakeEdge(p4, p1).Edge(),
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
    shell = minimal_surface_from_wires_minimal_like(
        wire1, wire2, n=100, m=100, shrink_ratio=0.7
    )

    # 表示
    display, start_display, add_menu, add_function_to_menu = init_display()
    display.DisplayShape(wire1, color="red")
    display.DisplayShape(wire2, color="blue")
    display.DisplayShape(shell, update=True)
    display.FitAll()
    start_display()
