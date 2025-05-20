import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from OCC.Core.TColgp import TColgp_Array1OfPnt2d, TColgp_HArray1OfPnt2d
from OCC.Core.Geom2dAPI import Geom2dAPI_PointsToBSpline
from OCC.Core.Geom2dAPI import Geom2dAPI_Interpolate
from OCC.Core.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCC.Core.GeomAPI import GeomAPI_Interpolate
from OCC.Core.gp import gp_Pnt2d

if __name__ == "__main__":
    """
    閉じたSpline曲線を作成し、Matplotlibでプロットする
    points: [(x1, y1), (x2, y2), ...] のリスト
    """

    # 制御点
    control_points = [
        (0, 0),
        (1, 2),
        (3, 3),
        (4, 1),
        (2, -1)
    ]

    # 点列を分解
    points = np.array(control_points)
    x_array, y_array = points[:, 0], points[:, 1]

    # 閉じるために始点を終点として追加
    x_array = np.append(x_array, x_array[0])
    y_array = np.append(y_array, y_array[0])

    # 点列をTColgp_Array1OfPnt2dに変換
    num_points = len(control_points)
    array = TColgp_Array1OfPnt2d(1, num_points)  # +1で始点を終点として追加
    for i, (x, y) in enumerate(control_points, start=1):
        array.SetValue(i, gp_Pnt2d(x, y))
    # 始点を終点として追加
    #array.SetValue(num_points + 1, array.Value(1))

    # スプライン曲線を生成
    spline_curve = Geom2dAPI_PointsToBSpline(array).Curve()
    
    harray = TColgp_HArray1OfPnt2d(array)
    
    # Interpolateで周期的スプラインを生成
    periodic = True
    tolerance = 1e-6
    interpolator = Geom2dAPI_Interpolate(harray, periodic, tolerance)
    interpolator.Perform()
    spline_curve = interpolator.Curve()

    # パラメータ（t）を生成
    t = np.linspace(0, 1, num_points + 1)

    # スプライン補間
    spline_x = make_interp_spline(t, x_array, k=3)  # 3次スプライン
    spline_y = make_interp_spline(t, y_array, k=3)

    # 補間点を生成
    t_new = np.linspace(0, 1, 300)  # 補間点の数を固定
    x_new = spline_x(t_new)
    y_new = spline_y(t_new)

    # スプライン曲線をプロット用にサンプリング
    num_samples = 300
    t_values = np.linspace(spline_curve.FirstParameter(), spline_curve.LastParameter(), num_samples)
    x_values = []
    y_values = []
    for t in t_values:
        point = spline_curve.Value(t)
        x_values.append(point.X())
        y_values.append(point.Y())

    # プロット
    plt.figure(figsize=(6, 6))
    plt.plot(x_new, y_new, label="Scipy Interpolate - Closed Spline", color="red")
    plt.plot(x_values, y_values, label="Geom2dAPI_Interpolate - Closed Spline", color="blue")
    plt.scatter(*zip(*control_points), color="red", label="Control Points")
    plt.legend()
    plt.axis("equal")
    plt.title("Closed Spline Curve")
    plt.show()
