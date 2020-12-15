import numpy as np

from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Ax3, gp_XY
from OCC.Core.gp import gp_Pnt, gp_Vec, gp_Dir, gp_XYZ
from OCC.Core.gp import gp_Trsf, gp_Quaternion

axs = gp_Ax3()

#ax1 = gp_Ax3(gp_Pnt(1, 2, 3), gp_Dir(0.5, 1.0, 1.5))
#ax1 = gp_Ax3(gp_Pnt(1, 2, 3), gp_Dir(1.0, 1.0, 0.0))
ax1 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0.5, 1.0, 1.5))
trf = gp_Trsf()
trf.SetTransformation(ax1, axs)
print(trf)
print(trf.DumpJsonToString())
print(trf.GetRotation(gp_XYZ(*axs.Direction().Coord())))
print(trf.GetRotation(gp_XYZ(*axs.XDirection().Coord())))
print(trf.GetRotation(gp_XYZ(*axs.YDirection().Coord())))

#ax2 = gp_Ax3(gp_Pnt(-1, -2, -3), gp_Dir(0, 0, 1))
#ax2 = gp_Ax3(gp_Pnt(0, 0, 0), gp_Dir(0, 0, 1))
ax2 = gp_Ax3(gp_Pnt(0, 0, 1), gp_Dir(0, 0, 1))
trf2 = gp_Trsf()
trf2.SetTransformation(ax2, axs)
print(trf2.DumpJsonToString())

ax2.Transform(trf)
trf2 = gp_Trsf()
trf2.SetTransformation(ax2, axs)
print(trf2.DumpJsonToString())


def print_axs(ax=gp_Ax3()):
    print(ax.Location())
    # <class 'gp_Pnt'>


class PrintAxs(object):

    def __init__(self):
        ax = gp_Ax3()
        print(ax.Location())
        # <class 'gp_Pnt'>


if __name__ == "__main__":
    print(axs.Location())
    # <class 'gp_Pnt'>
    print_axs()
    PrintAxs()
