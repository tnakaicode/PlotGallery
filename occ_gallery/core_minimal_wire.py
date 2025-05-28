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
    wire1: TopoDS_Wire,
    wire2: TopoDS_Wire,
    n: int = 100,
    m: int = 30,
    shrink_ratio=0.5,
    return_area=False,
):
    """Create a minimal-like surface between two wires.
    This function generates a minimal-like surface by sampling points on two wires

    Args:
        wire1 (TopoDS_Wire):
        wire2 (TopoDS_Wire):
        n (int, optional): Defaults to 100.
        m (int, optional): \Defaults to 30.
        shrink_ratio (float, optional): Defaults to 0.5.
        return_area (bool, optional): Defaults to False.
    Returns:
        _type_: _description_
    """
    pts1 = sample_points_on_wire(wire1, n)
    pts2 = sample_points_on_wire(wire2, n)
    grid = []
    for k in range(m):
        t = k / (m - 1)
        s = (np.cosh((t - 0.5) * 2) - np.cosh(1)) / (np.cosh(0) - np.cosh(1))
        ring = []
        center = (1 - t) * np.mean(
            [[p.X(), p.Y(), p.Z()] for p in pts1], axis=0
        ) + t * np.mean([[p.X(), p.Y(), p.Z()] for p in pts2], axis=0)
        for i in range(n):
            p1 = np.array([pts1[i].X(), pts1[i].Y(), pts1[i].Z()])
            p2 = np.array([pts2[i].X(), pts2[i].Y(), pts2[i].Z()])
            p = (1 - t) * p1 + t * p2
            p = p + (center - p) * s * shrink_ratio
            ring.append(gp_Pnt(*p))
        grid.append(ring)
    edges = []
    area = 0.0
    for k in range(m - 1):
        for i in range(n):
            i_next = (i + 1) % n
            p1 = grid[k][i]
            p2 = grid[k + 1][i]
            p3 = grid[k + 1][i_next]
            p4 = grid[k][i_next]
            # 三角形1
            edges.append(
                BRepBuilderAPI_MakeWire(
                    BRepBuilderAPI_MakeEdge(p1, p2).Edge(),
                    BRepBuilderAPI_MakeEdge(p2, p3).Edge(),
                    BRepBuilderAPI_MakeEdge(p3, p1).Edge(),
                ).Wire()
            )
            # 三角形2
            edges.append(
                BRepBuilderAPI_MakeWire(
                    BRepBuilderAPI_MakeEdge(p1, p3).Edge(),
                    BRepBuilderAPI_MakeEdge(p3, p4).Edge(),
                    BRepBuilderAPI_MakeEdge(p4, p1).Edge(),
                ).Wire()
            )
            # 面積計算（2三角形分）
            # 三角形1
            v1 = np.array([p2.X() - p1.X(), p2.Y() - p1.Y(), p2.Z() - p1.Z()])
            v2 = np.array([p3.X() - p1.X(), p3.Y() - p1.Y(), p3.Z() - p1.Z()])
            area += 0.5 * np.linalg.norm(np.cross(v1, v2))
            # 三角形2
            v1 = np.array([p3.X() - p1.X(), p3.Y() - p1.Y(), p3.Z() - p1.Z()])
            v2 = np.array([p4.X() - p1.X(), p4.Y() - p1.Y(), p4.Z() - p1.Z()])
            area += 0.5 * np.linalg.norm(np.cross(v1, v2))
    print(f"Total area: {area:.4f}")
    sewing = BRepBuilderAPI_Sewing()
    for w in edges:
        face = BRepBuilderAPI_MakeFace(w)
        sewing.Add(face.Face())
    sewing.Perform()
    shell = sewing.SewedShape()
    if return_area:
        return shell, area
    else:
        return shell


def minimal_surface_on_single_wire(wire: TopoDS_Wire, n: int = 100, return_area=False):
    """
    1つのWireに張る極小曲面近似（三角形ファン）を生成
    Args:
        wire (TopoDS_Wire): 閉じたワイヤ
        n (int): サンプリング点数
        return_area (bool): Trueなら面積も返す
    Returns:
        shell (TopoDS_Shape): 曲面シェル
        area (float, optional): 面積
    """
    pts = sample_points_on_wire(wire, n)
    # 重心
    center = np.mean([[p.X(), p.Y(), p.Z()] for p in pts], axis=0)
    center_pnt = gp_Pnt(*center)
    edges = []
    area = 0.0
    for i in range(n):
        i_next = (i + 1) % n
        p1 = pts[i]
        p2 = pts[i_next]
        # 三角形ワイヤ
        wire_tri = BRepBuilderAPI_MakeWire(
            BRepBuilderAPI_MakeEdge(p1, p2).Edge(),
            BRepBuilderAPI_MakeEdge(p2, center_pnt).Edge(),
            BRepBuilderAPI_MakeEdge(center_pnt, p1).Edge(),
        ).Wire()
        edges.append(wire_tri)
        # 面積計算
        v1 = np.array([p2.X() - p1.X(), p2.Y() - p1.Y(), p2.Z() - p1.Z()])
        v2 = np.array(
            [center_pnt.X() - p1.X(), center_pnt.Y() - p1.Y(), center_pnt.Z() - p1.Z()]
        )
        area += 0.5 * np.linalg.norm(np.cross(v1, v2))
    # Sewingでシェル化
    sewing = BRepBuilderAPI_Sewing()
    for w in edges:
        face = BRepBuilderAPI_MakeFace(w)
        sewing.Add(face.Face())
    sewing.Perform()
    shell = sewing.SewedShape()
    if return_area:
        return shell, area
    else:
        return shell


# --- 使用例 ---
if __name__ == "__main__":
    display, start_display, add_menu, add_function_to_menu = init_display()
    # 例として2つの円ワイヤを生成
    from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
    from OCC.Core.GC import GC_MakeCircle, GC_MakeEllipse
    from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire

    n = 100
    # 下円
    ax2_1 = gp_Ax2(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
    circle1 = GC_MakeEllipse(ax2_1, 1.0, 1.0).Value()
    edge1 = BRepBuilderAPI_MakeEdge(circle1).Edge()
    wire1 = BRepBuilderAPI_MakeWire(edge1).Wire()
    # 上円（ずらして傾ける例）
    ax2_2 = gp_Ax2(gp_Pnt(0.5, 0.5, 2.0), gp_Dir(0.2, 0.2, 1.0), gp_Dir(0, 1, 0))
    circle2 = GC_MakeCircle(ax2_2, 1.0).Value()
    edge2 = BRepBuilderAPI_MakeEdge(circle2).Edge()
    wire2 = BRepBuilderAPI_MakeWire(edge2).Wire()

    # 極小曲面近似
    shell = minimal_surface_from_wires_minimal_like(
        wire1, wire2, n=100, m=100, shrink_ratio=0.4
    )

    shell1, area = minimal_surface_on_single_wire(wire1, n=100, return_area=True)
    print(f"面積: {area:.4f}")
    display.DisplayShape(shell1, update=True)

    # 表示
    display.DisplayShape(wire1, color="red")
    display.DisplayShape(wire2, color="blue1")
    display.DisplayShape(shell, update=True)
    display.FitAll()
    start_display()
