import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve

# パラメータ
R = 1.0  # 円盤の半径
d = 2.0  # 円盤間の距離
n = 100  # 分割数


# aを自動調整
def eq(a):
    return a * np.cosh((d / 2) / a) - R


a_init = 0.5
a = fsolve(eq, a_init)[0]

# z方向の座標
z = np.linspace(-d / 2, d / 2, n)
# カテナリー関数
r = a * np.cosh(z / a)

# 円周方向
theta = np.linspace(0, 2 * np.pi, n)
Z, Theta = np.meshgrid(z, theta)
Rr = a * np.cosh(Z / a)

# 極座標→直交座標
X = Rr * np.cos(Theta)
Y = Rr * np.sin(Theta)

# プロット
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection="3d")
ax.plot_surface(X, Y, Z, cmap="viridis", alpha=0.8)

# 円盤も描画（極小曲面の端と一致）
circle_z1 = np.full_like(theta, -d / 2)
circle_z2 = np.full_like(theta, d / 2)
ax.plot(r[0] * np.cos(theta), r[0] * np.sin(theta), circle_z1, color="red")
ax.plot(r[-1] * np.cos(theta), r[-1] * np.sin(theta), circle_z2, color="red")

ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title("Minimal Surface between Two Disks")
plt.show()
