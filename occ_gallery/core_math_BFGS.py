from OCC.Core.math import math_BFGS, math_Vector, math_BissecNewton
from OCC.Core.gp import gp_Pnt

# 定義する関数とその勾配


class MyFunction:
    def __init__(self):
        pass

    def Value(self, point):
        x = point.Value(1)
        y = point.Value(2)
        return (x - 3)**2 + (y + 2)**2

    def Gradient(self, point, grad):
        x = point.Value(1)
        y = point.Value(2)
        grad.SetValue(1, 2 * (x - 3))
        grad.SetValue(2, 2 * (y + 2))


# 初期化
nb_variables = 2
tolerance = 1e-8
max_iterations = 200

bfgs = math_BFGS(nb_variables, tolerance, max_iterations)

# 初期点
starting_point = math_Vector(1, nb_variables, 0.0)
#starting_point.Set(1, 1.0)  # x = 0
starting_point.Set(1, 1, math_Vector(1, 1, 10.0))  # x = 0
starting_point.Set(1, 2, math_Vector(1, 2, 11.0))  # y = 0
print()
print(starting_point.Min())
print(f"初期点: x = {starting_point.Value(1).GetValue()}, y = {starting_point.Value(2)}")

# 関数のインスタンス
function = MyFunction()

# 最適化を実行
bfgs.Perform(function, starting_point)

# 結果を取得
if bfgs.IsDone():
    location = bfgs.Location()
    minimum = bfgs.Minimum()
    print(f"最小値の位置: x = {location.Value(1)}, y = {location.Value(2)}")
    print(f"最小値: {minimum}")
else:
    print("最適化に失敗しました。")
