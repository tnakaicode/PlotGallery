import numpy as np
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2
from OCC.Core.BRepBuilderAPI import (
    BRepBuilderAPI_MakeFace,
    BRepBuilderAPI_MakeWire,
    BRepBuilderAPI_MakeEdge,
)
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_Sewing
from OCC.Core.BRep import BRep_Builder, BRep_Tool
from OCC.Core.TopoDS import TopoDS_Compound
from OCC.Display.SimpleGui import init_display

# パラメータ
R = 1.0
d = 2.0
n = 60  # 分割数（多すぎると重い）

shift_x = 0.5
shift_y = 0.5
n_vec = np.array([0.2, 0.2, 1.0])
n_vec = n_vec / np.linalg.norm(n_vec)

from scipy.optimize import fsolve


def eq(a):
    return a * np.cosh((d / 2) / a) - R


a_init = 0.5
a = fsolve(eq, a_init)[0]

z = np.linspace(-d / 2, d / 2, n)
r = a * np.cosh(z / a)
center_x = np.linspace(0, shift_x, n)
center_y = np.linspace(0, shift_y, n)
center_z = z
n0 = np.array([0, 0, 1])
normals = np.outer(1 - (z + d / 2) / d, n0) + np.outer((z + d / 2) / d, n_vec)
normals = normals / np.linalg.norm(normals, axis=1)[:, None]
theta = np.linspace(0, 2 * np.pi, n)


def get_radius_for_disk(center, normal, disk_center, disk_normal, R):
    # 曲面断面の中心(center)・法線(normal)と、円盤の中心・法線(disk_center, disk_normal)が与えられたとき
    # その断面上で「円盤の中心から半径R」になる点までの距離を返す
    # 断面法線と円盤法線が一致していればr=R
    # ずれている場合は、断面中心から円盤面までの距離を使って補正
    # 断面中心から円盤面までの距離
    v = np.array(disk_center) - np.array(center)
    h = np.dot(v, disk_normal)
    # 断面法線と円盤法線のなす角
    cos_theta = np.dot(normal, disk_normal)
    # 断面上で円盤と交わる円の半径
    if abs(cos_theta) < 1e-8:
        # ほぼ直交の場合
        return R
    r = np.sqrt(max(R**2 - (h / cos_theta) ** 2, 0))
    return r


# 曲面点リスト
points = []
for i in range(n):
    nxi, nyi, nzi = normals[i]
    if abs(nzi) < 0.99:
        v1 = np.cross([0, 0, 1], [nxi, nyi, nzi])
    else:
        v1 = np.cross([1, 0, 0], [nxi, nyi, nzi])
    v1 = v1 / np.linalg.norm(v1)
    v2 = np.cross([nxi, nyi, nzi], v1)
    v2 = v2 / np.linalg.norm(v2)
    ring = []
    for t in theta:
        x = center_x[i] + r[i] * (np.cos(t) * v1[0] + np.sin(t) * v2[0])
        y = center_y[i] + r[i] * (np.cos(t) * v1[1] + np.sin(t) * v2[1])
        z_ = center_z[i] + r[i] * (np.cos(t) * v1[2] + np.sin(t) * v2[2])
        ring.append(gp_Pnt(x, y, z_))
    points.append(ring)

# メッシュ状にエッジを作成
edges = []
for i in range(n - 1):
    for j in range(n - 1):
        # 4点で四角形
        p1 = points[i][j]
        p2 = points[i + 1][j]
        p3 = points[i + 1][j + 1]
        p4 = points[i][j + 1]
        # 2つの三角形に分割
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

# 下円盤
from OCC.Core.GC import GC_MakeCircle
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace

ax2_down = gp_Ax2(gp_Pnt(0, 0, -d / 2), gp_Dir(0, 0, 1))
circle_down = GC_MakeCircle(ax2_down, R).Value()
edge_down = BRepBuilderAPI_MakeEdge(circle_down).Edge()
wire_down = BRepBuilderAPI_MakeWire(edge_down).Wire()
face_down = BRepBuilderAPI_MakeFace(wire_down).Face()

# 上円盤
ax2_up = gp_Ax2(gp_Pnt(shift_x, shift_y, d / 2), gp_Dir(*n_vec))
circle_up = GC_MakeCircle(ax2_up, R).Value()
edge_up = BRepBuilderAPI_MakeEdge(circle_up).Edge()
wire_up = BRepBuilderAPI_MakeWire(edge_up).Wire()
face_up = BRepBuilderAPI_MakeFace(wire_up).Face()

# Compoundでまとめる
builder = BRep_Builder()
compound = TopoDS_Compound()
builder.MakeCompound(compound)
builder.Add(compound, shell)
builder.Add(compound, face_down)
builder.Add(compound, face_up)

# 表示
display, start_display, add_menu, add_function_to_menu = init_display()
display.DisplayShape(compound, update=True)
display.FitAll()
start_display()
