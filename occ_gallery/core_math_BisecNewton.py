from OCC.Core.math import math_BissecNewton, math_FunctionWithDerivative

# 定義する関数 (math_FunctionWithDerivative を継承)
class MyFunction(math_FunctionWithDerivative):
    def __init__(self):
        #math_FunctionWithDerivative.__init__(self)
        #super(MyFunction, self).__init__()  # 親クラスの初期化を呼び出す
        pass
        
    def Value(self, x):
        # 関数 f(x) = x^2 - 4
        return x**2 - 4

    def Derivative(self, x):
        # 関数の導関数 f'(x) = 2x
        return 2 * x

# 初期化
tolerance = 1e-8
solver = math_BissecNewton(tolerance)

# 初期値と範囲
x_min = 0.0  # 範囲の下限
x_max = 5.0  # 範囲の上限
initial_guess = 2.0  # 初期推定値

# 関数のインスタンス
F = MyFunction()

# 解を求める
solver.Perform(F, x_min, x_max, initial_guess)

# 結果を取得
if solver.IsDone():
    root = solver.Root()
    print(f"方程式の解: x = {root}")
else:
    print("解を見つけることができませんでした。")