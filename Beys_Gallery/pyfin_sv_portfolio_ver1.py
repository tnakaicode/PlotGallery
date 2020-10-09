import numpy as np
import cvxpy as cvx
import pandas as pd
import numpy.linalg as lin
import scipy.optimize as opt
import scipy.stats as st
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as pol
from matplotlib.font_manager import FontProperties
import sys

# 収益率データの読み込み
R = pd.read_csv('asset_return_data.csv', index_col=0)
T = R.shape[0]
N = R.shape[1]
Mu = R.mean().values
Return_Dev = (R - Mu).values / np.sqrt(T)

# 下方半分散最小化問題の設定
Weight = cvx.Variable(N)
Deviation = cvx.Variable(T)
Target_Return = cvx.Parameter(nonneg=True)
Risk_Semivariance = cvx.sum_squares(Deviation)
Opt_Portfolio = cvx.Problem(cvx.Minimize(Risk_Semivariance),
                            [Weight.T * Mu == Target_Return,
                             cvx.sum(Weight) == 1.0,
                             Weight >= 0.0,
                             Deviation >= 0.0,
                             Return_Dev * Weight + Deviation >= 0.0])

# 最小下方半分散フロンティアの計算
V_Target = np.linspace(Mu.min(), Mu.max(), num=250)
V_Risk = np.zeros(V_Target.shape)
for idx, Target_Return.value in enumerate(V_Target):
    Opt_Portfolio.solve(solver=cvx.ECOS)
    V_Risk[idx] = np.sqrt(Risk_Semivariance.value)

# 最小下方半分散フロンティアのグラフの作成
fig1 = plt.figure(1, facecolor='w')
plt.plot(V_Risk, V_Target, 'k-')
plt.plot(np.sqrt(((R[R <= Mu] - Mu) ** 2).sum().values / T), Mu, 'kx')
plt.legend([u'最小下方半分散フロンティア', u'個別資産'],
           loc='best', frameon=False)
plt.xlabel(u'下方半分散の平方根(%)')
plt.ylabel(u'期待収益率(%)')
plt.show()
