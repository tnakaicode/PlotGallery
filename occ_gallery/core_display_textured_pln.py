#!/usr/bin/env python

# Copyright 2009-2015 Thomas Paviot (tpaviot@gmail.com)
##
# This file is part of pythonOCC.
##
# pythonOCC is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
##
# pythonOCC is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
##
# You should have received a copy of the GNU Lesser General Public License
# along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.

import os
import numpy as np
import matplotlib.pyplot as plt

from OCC.Core.gp import gp_Pln, gp_Ax3
from OCC.Extend.ShapeFactory import make_face
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakeCylinder

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


class Texture(object):
    """
    This class encapsulates the necessary texture properties:
    Filename, toScaleU, etc.
    """

    def __init__(self, filename):
        if not os.path.isfile(filename):
            raise IOError("File %s not found.\n" % filename)
        self._filename = filename
        self._toScaleU = 1.0
        self._toScaleV = 1.0
        self._toRepeatU = 1.0
        self._toRepeatV = 1.0
        self._originU = 0.0
        self._originV = 0.0

    def TextureScale(self, toScaleU, toScaleV):
        self._toScaleU = toScaleU
        self._toScaleV = toScaleV

    def TextureRepeat(self, toRepeatU, toRepeatV):
        self._toRepeatU = toRepeatU
        self._toRepeatV = toRepeatV

    def TextureOrigin(self, originU, originV):
        self._originU = originU
        self._originV = originV

    def GetProperties(self):
        return (
            self._filename,
            self._toScaleU,
            self._toScaleV,
            self._toRepeatU,
            self._toRepeatV,
            self._originU,
            self._originV,
        )


xs, xe = -100, 100
ys, ye = -100, 100
px = np.linspace(xs, xe, 100)
py = np.linspace(ys, ye, 200)
mesh = np.meshgrid(px, py)
name = "./images/texture.png"

plt.figure()
plt.contourf(*mesh, mesh[0])
plt.savefig(name, transparent=0.9)

#
# First create texture and a material
#
texture_filename = name
t = Texture(texture_filename)
#
# Displays a cylinder with a material and a texture
#
pln = make_face(gp_Pln(gp_Ax3()), xs, xe, ys, ye)
s = BRepPrimAPI_MakeCylinder(60, 200)
display.DisplayShape(pln, texture=t, update=True)
start_display()
