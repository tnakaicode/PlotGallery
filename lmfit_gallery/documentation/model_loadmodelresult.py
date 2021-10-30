"""
doc_model_loadmodelresult.py
============================


"""
# <examples/doc_model_loadmodelresult.py>
import matplotlib.pyplot as plt
import numpy as np

from lmfit.model import load_modelresult

data = np.loadtxt('model1d_gauss.dat')
x = data[:, 0]
y = data[:, 1]

result = load_modelresult('gauss_modelresult.sav')
print(result.fit_report())

plt.plot(x, y, 'o')
plt.plot(x, result.best_fit, '-')
plt.show()
# <end examples/doc_model_loadmodelresult.py>
