import numpy as np

from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Ax3
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir
from OCC.Core.gp import gp_Trsf

axs = gp_Ax3()

ax1 = gp_Ax3(gp_Pnt(1, 2, 3), gp_Dir(0, 0, 1))
trf = gp_Trsf()
trf.SetTransformation(ax1, axs)
print(trf.DumpJsonToString())

ax1 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0.5, 1.0, 1.5))
trf = gp_Trsf()
trf.SetTransformation(ax1, axs)
print(trf.DumpJsonToString())

ax1 = gp_Ax3(gp_Pnt(1, 2, 3), gp_Dir(0.5, 1.0, 1.5))
trf = gp_Trsf()
trf.SetTransformation(ax1, axs)
print(trf.DumpJsonToString())
