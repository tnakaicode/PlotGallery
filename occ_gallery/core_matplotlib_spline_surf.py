import numpy as np
import matplotlib.pyplot as plt
from OCC.Core.TColgp import TColgp_Array2OfPnt
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.gp import gp_Pnt

# 制御点グリッド（例：5x5の格子、u方向・v方向ともに閉じる）
control_points = np.array([
    [(np.cos(2 * np.pi * i / 5) * 2 + np.sin(2 * np.pi * j / 5), np.sin(2 * np.pi *
      i / 5) * 2 + np.cos(2 * np.pi * j / 5), np.sin(i + j)) for j in range(5)]
    for i in range(5)
])

n_u, n_v = control_points.shape[:2]
array = TColgp_Array2OfPnt(1, n_u, 1, n_v)
for i in range(n_u):
    for j in range(n_v):
        x, y, z = control_points[i, j]
        array.SetValue(i + 1, j + 1, gp_Pnt(x, y, z))

# BSplineサーフェス生成
surf_api = GeomAPI_PointsToBSplineSurface(
    array, True, True, 3, 3)  # u/v方向とも周期的
surf = surf_api.Surface()

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

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import bisplrep, bisplev

# 制御点グリッド（例：5x5の格子、u/v方向とも閉じる）
control_points = np.array([
    [(np.cos(2 * np.pi * i / 5) * 2 + np.sin(2 * np.pi * j / 5), np.sin(2 * np.pi *
      i / 5) * 2 + np.cos(2 * np.pi * j / 5), np.sin(i + j)) for j in range(5)]
    for i in range(5)
])
n_u, n_v = control_points.shape[:2]
x = control_points[:, :, 0]
y = control_points[:, :, 1]
z = control_points[:, :, 2]

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
