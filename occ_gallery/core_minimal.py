import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# パラメータ
R = 1.0  # 円盤の半径
d = 2.0  # 円盤間の距離
n = 100  # 分割数

# 上円盤の中心のxyシフトと法線ベクトル
shift_x = 0.5
shift_y = 0.5
# 上円盤の法線ベクトル（単位ベクトルにしてください）
n_vec = np.array([0.2, 0.2, 1.0])
n_vec = n_vec / np.linalg.norm(n_vec)


# aを自動調整（下円盤と同じ半径で合わせる）
def eq(a):
    return a * np.cosh((d / 2) / a) - R


a_init = 0.5
a = fsolve(eq, a_init)[0]

# z方向の座標
z = np.linspace(-d / 2, d / 2, n)
# カテナリー関数
r = a * np.cosh(z / a)

# 各z断面で中心座標を線形補間
center_x = np.linspace(0, shift_x, n)
center_y = np.linspace(0, shift_y, n)
center_z = z

# 各z断面で法線ベクトルを線形補間（今回はz方向からn_vecへ線形補間）
n0 = np.array([0, 0, 1])
normals = np.outer(1 - (z + d / 2) / d, n0) + np.outer((z + d / 2) / d, n_vec)
normals = normals / np.linalg.norm(normals, axis=1)[:, None]

# 円周方向
theta = np.linspace(0, 2 * np.pi, n)

# 曲面点を計算
X = np.zeros((n, n))
Y = np.zeros((n, n))
Z = np.zeros((n, n))

for i in range(n):
    # 各断面の法線ベクトル
    nxi, nyi, nzi = normals[i]
    # 任意の法線に垂直な2ベクトルを作る
    if abs(nzi) < 0.99:
        v1 = np.cross([0, 0, 1], [nxi, nyi, nzi])
    else:
        v1 = np.cross([1, 0, 0], [nxi, nyi, nzi])
    v1 = v1 / np.linalg.norm(v1)
    v2 = np.cross([nxi, nyi, nzi], v1)
    v2 = v2 / np.linalg.norm(v2)
    # 円周上の点
    X[i, :] = center_x[i] + r[i] * (np.cos(theta) * v1[0] + np.sin(theta) * v2[0])
    Y[i, :] = center_y[i] + r[i] * (np.cos(theta) * v1[1] + np.sin(theta) * v2[1])
    Z[i, :] = center_z[i] + r[i] * (np.cos(theta) * v1[2] + np.sin(theta) * v2[2])

# プロット
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8)

# 円盤も描画
# 下円盤
ax.plot(
    R * np.cos(theta),
    R * np.sin(theta),
    np.full_like(theta, -d / 2),
    color="red",
)
# 上円盤
# 上円盤の中心と法線で円を描く
n1 = n_vec
if abs(n1[2]) < 0.99:
    v1 = np.cross([0, 0, 1], n1)
else:
    v1 = np.cross([1, 0, 0], n1)
v1 = v1 / np.linalg.norm(v1)
v2 = np.cross(n1, v1)
v2 = v2 / np.linalg.norm(v2)
cx, cy, cz = shift_x, shift_y, d / 2
x_up = cx + R * (np.cos(theta) * v1[0] + np.sin(theta) * v2[0])
y_up = cy + R * (np.cos(theta) * v1[1] + np.sin(theta) * v2[1])
z_up = cz + R * (np.cos(theta) * v1[2] + np.sin(theta) * v2[2])
ax.plot(x_up, y_up, z_up, color="red")

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Minimal Surface between Two (Possibly Tilted) Disks")
plt.show()
