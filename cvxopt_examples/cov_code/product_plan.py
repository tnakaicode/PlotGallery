import cvxpy as cp  # まずはモジュールの読み込み
x1, x2 = cp.Variable(), cp.Variable()  # 決定変数を定義
obj = cp.Maximize(20 * x1 + 60 * x2)  # 目的関数を記述
cons = [5 * x1 + 4 * x2 <= 80,
        2 * x1 + 4 * x2 <= 40,
        2 * x1 + 8 * x2 <= 64,
        x1 >= 0,
        x2 >= 0]  # ここまでが制約の記述
P = cp.Problem(obj, cons)  # 最適化問題を定義
P.solve(verbose=True)  # 求解
print(x1.value, x2.value)  # 最適解の出力
