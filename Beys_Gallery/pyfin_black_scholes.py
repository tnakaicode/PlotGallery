import numpy as np
import cvxpy as cvx
import pandas as pd
import numpy.linalg as lin
import scipy.optimize as opt
import scipy.stats as st
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import sys

# Black-Scholeの公式によるヨーロピアン・コールオプション価格の計算
S = 100.0
K = 100.0
r = 0.01
v = 0.20
T = 0.50
d1 = (np.log(S / K) + (r + 0.5 * v ** 2) * T) / (v * np.sqrt(T))
d2 = d1 - v * np.sqrt(T)
BS_Formula = S * st.norm.cdf(d1) - K * np.exp(-r * T) * st.norm.cdf(d2)
