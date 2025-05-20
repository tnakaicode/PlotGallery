import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

if __name__ == "__main__":

    """
    閉じたSpline曲線を作成し、Matplotlibでプロットする
    points: [(x1, y1), (x2, y2), ...] のリスト
    num_samples: 補間点の数
    """
    control_points = [
        (0, 0),
        (1, 2),
        (3, 3),
        (4, 1),
        (2, -1)
    ]

    # 点列を分解
    points = np.array(control_points)
    x, y = points[:, 0], points[:, 1]

    # 閉じるために始点を終点として追加
    x = np.append(x, x[0])
    y = np.append(y, y[0])

    # パラメータ（t）を生成
    t = np.linspace(0, 1, len(x))

    # スプライン補間
    spline_x = make_interp_spline(t, x, k=3)  # 3次スプライン
    spline_y = make_interp_spline(t, y, k=3)

    # 補間点を生成
    t_new = np.linspace(0, 1, 300)  # 補間点の数を固定
    x_new = spline_x(t_new)
    y_new = spline_y(t_new)

    # プロット
    plt.figure(figsize=(6, 6))
    plt.plot(x_new, y_new, label="Closed Spline", color="blue")
    plt.scatter(x, y, color="red", label="Control Points")
    plt.legend()
    plt.axis("equal")
    plt.title("Closed Spline Curve")
    plt.show()
