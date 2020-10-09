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

# 収益率データの読み込みとベンチマークの生成
R = pd.read_csv('asset_return_data.csv', index_col=0)
R = R.asfreq(pd.infer_freq(R.index))
T = R.shape[0]
N = R.shape[1]
np.random.seed(8888)
BenchmarkIndex = R.dot(np.tile(1.0 / N, N)) + st.norm(0.0, 3.0).rvs(T)

# トラッキングエラー最小化問題のバックテスト
MovingWindow = 96
BackTesting = T - MovingWindow
V_Tracking = np.zeros(BackTesting)
Weight = cvx.Variable(N)
Error = cvx.Variable(MovingWindow)
TrackingError = cvx.sum_squares(Error)
Asset_srT = R / np.sqrt(MovingWindow)
Index_srT = BenchmarkIndex / np.sqrt(MovingWindow)
for Month in range(0, BackTesting):
    Asset = Asset_srT.values[Month:(Month + MovingWindow), :]
    Index = Index_srT.values[Month:(Month + MovingWindow)]
    Min_TrackingError = cvx.Problem(cvx.Minimize(TrackingError),
                                    [Index - Asset * Weight == Error,
                                     cvx.sum(Weight) == 1.0,
                                     Weight >= 0.0])
    Min_TrackingError.solve(solver=cvx.ECOS)
    V_Tracking[Month] = R.values[Month + MovingWindow, :].dot(Weight.value)

# バックテストの結果のグラフ
fig1 = plt.figure(1, facecolor='w')
plt.plot(list(range(1, BackTesting + 1)), BenchmarkIndex[MovingWindow:], 'k-')
plt.plot(list(range(1, BackTesting + 1)), V_Tracking, 'k--')
plt.legend([u'ベンチマーク・インデックス', u'インデックス・ファンド'],
           loc='best', frameon=False)
plt.xlabel(u'運用期間(年）')
plt.ylabel(u'収益率(%)')
plt.xticks(list(range(12, BackTesting + 1, 12)),
           pd.date_range(R.index[MovingWindow], periods=BackTesting // 12,
                         freq='AS').year)
plt.show()
