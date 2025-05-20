import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import bisplrep, bisplev
from OCC.Core.TColgp import TColgp_Array2OfPnt, TColgp_HArray2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomAbs import GeomAbs_C0, GeomAbs_C1, GeomAbs_C2
from OCC.Core.GeomAbs import GeomAbs_G1, GeomAbs_G2
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Algo
from OCC.Core.gp import gp_Pnt
from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()

# 制御点グリッド（例：5x5の格子、u/v方向とも閉じる）
nx, ny = 10, 11
control_points = np.array([
    [
        (
            np.cos(2 * np.pi * i / nx) * 2 + np.sin(2 * np.pi * j / ny),
            np.sin(2 * np.pi * i / nx) * 2 + np.cos(2 * np.pi * j / ny),
            np.sin(np.pi * j / ny)
        ) for i in range(nx)
    ] for j in range(ny)
])

n_u, n_v = control_points.shape[:2]
x = control_points[:, :, 0]
y = control_points[:, :, 1]
z = control_points[:, :, 2]

array = TColgp_Array2OfPnt(1, n_u, 1, n_v)
for ix in range(n_u):
    for iy in range(n_v):
        xv, yv, zv = control_points[ix, iy]
        array.SetValue(ix + 1, iy + 1, gp_Pnt(xv, yv, zv))
        display.DisplayShape(gp_Pnt(xv, yv, zv))

harray = TColgp_HArray2OfPnt(array)

# BSplineサーフェス生成
surf_G1_api = GeomAPI_PointsToBSplineSurface(array, 3, 8, GeomAbs_C0, 0.1E-6)
surf_G1 = surf_G1_api.Surface()

surf_G2_api = GeomAPI_PointsToBSplineSurface(array, 3, 8, GeomAbs_G2, 0.1E-6)
surf_G2 = surf_G2_api.Surface()

display.DisplayShape(surf_G1, color='red', transparency=0.5)
display.DisplayShape(surf_G2, color='blue1', transparency=0.5)
display.FitAll()
start_display()

# サーフェスをサンプリングしてプロット
# uu = np.linspace(surf.FirstUParameter(), surf.LastUParameter(), 50)
# vv = np.linspace(surf.FirstVParameter(), surf.LastVParameter(), 50)
# X, Y, Z = [], [], []
# for u in uu:
#    row_x, row_y, row_z = [], [], []
#    for v in vv:
#        p = surf.Value(u, v)
#        row_x.append(p.X())
#        row_y.append(p.Y())
#        row_z.append(p.Z())
#    X.append(row_x)
#    Y.append(row_y)
#    Z.append(row_z)
# X, Y, Z = np.array(X), np.array(Y), np.array(Z)
#
# fig = plt.figure(figsize=(7, 6))
# ax = fig.add_subplot(111, projection='3d')
# ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.7)
# ax.scatter(control_points[:,:,0], control_points[:,:,1], control_points[:,:,2], color='red', label='Control Points')
# ax.set_title("OCC: Closed BSpline Surface")
# plt.legend()


# パラメータ
u = np.linspace(0, 1, n_u)
v = np.linspace(0, 1, n_v)

# 近似Bスプラインサーフェス
tck = bisplrep(x, y, z, s=0, kx=3, ky=3)
uu = np.linspace(0, 1, 50)
vv = np.linspace(0, 1, 50)
UU, VV = np.meshgrid(uu, vv)
ZZ = bisplev(uu, vv, tck)

fig = plt.figure(figsize=(7, 6))
ax = fig.add_subplot(111, projection='3d')
ax.plot_surface(x, y, z, color='gray', alpha=0.3, label='Control Net')
ax.plot_surface(UU, VV, ZZ, cmap='plasma', alpha=0.7)
ax.scatter(x, y, z, color='red', label='Control Points')
ax.set_title("scipy: Closed BSpline Surface (approximate)")
plt.legend()
plt.show()
