#!/usr/bin/env python

# Copyright 2009-2014 Jelle Feringa (jelleferinga@gmail.com)
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

from __future__ import print_function
import imp

import sys


from OCC.Display.SimpleGui import init_display
from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Vec
from OCC.Core.gp import gp_Ax1, gp_Ax2, gp_Ax3
from OCC.Core.gp import gp_Trsf, gp_Quaternion
from OCC.Core.gp import gp_Pln
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Extend.ShapeFactory import make_edge, make_face

display, start_display, add_menu, add_function_to_menu = init_display()


def vector_to_point(self):
    return gp_Pnt(self.XYZ())


def point_to_vector(self):
    return gp_Vec(self.XYZ())


def dir_to_vec(self):
    return gp_Vec(self)


def pnt_trf_vec(pnt=gp_Pnt(), vec=gp_Vec()):
    v = point_to_vector(pnt)
    v.Add(vec)
    return vector_to_point(v)


def make_line(pnt1, pnt2):
    return make_edge(pnt1, pnt2)


def make_plane(axs=gp_Ax3(),
               extent_x_min=-100.,
               extent_x_max=100.,
               extent_y_min=-100.,
               extent_y_max=100.,
               depth=0.):
    center = axs.Location()
    dir_normal = axs.Direction()
    vec_normal = dir_to_vec(dir_normal) 
    if depth != 0:
        center = center.add_vec(gp_Vec(0, 0, depth))
    PL = gp_Pln(center, dir_normal)
    face = make_face(PL,
                     extent_x_min,
                     extent_x_max,
                     extent_y_min,
                     extent_y_max)
    return face


def show_axs_pln(axs=gp_Ax3(), scale=100, name=None):
    pnt = axs.Location()
    dx = axs.XDirection()
    dy = axs.YDirection()
    dz = axs.Direction()
    vx = dir_to_vec(dx).Scaled(1 * scale)
    vy = dir_to_vec(dy).Scaled(1 * scale)
    vz = dir_to_vec(dz).Scaled(1 * scale)
    pnt_x = pnt_trf_vec(pnt, vx)
    pnt_y = pnt_trf_vec(pnt, vy)
    pnt_z = pnt_trf_vec(pnt, vz)
    lx, ly, lz = make_line(pnt, pnt_x), make_line(
        pnt, pnt_y), make_line(pnt, pnt_z)
    display.DisplayShape(pnt)
    display.DisplayShape(lx, color="RED")
    display.DisplayShape(ly, color="GREEN")
    display.DisplayShape(lz, color="BLUE1")
    if name != None:
        display.DisplayMessage(axs.Location(), name)


def axis():
    p1 = gp_Pnt(2.0, 3.0, 4.0)
    d = gp_Dir(4.0, 5.0, 6.0)
    a = gp_Ax3(p1, d)
    a_IsDirect = a.Direct()
    print("a is direct:", a_IsDirect)
    # a_XDirection = a.XDirection()
    # a_YDirection = a.YDirection()
    p2 = gp_Pnt(5.0, 3.0, 4.0)
    a2 = gp_Ax3(p2, d)
    a2.YReverse()
    # axis3 is now left handed
    a2_IsDirect = a2.Direct()
    print("a2 is direct:", a2_IsDirect)
    # a2_XDirection = a2.XDirection()
    # a2_YDirection = a2.YDirection()
    display.DisplayShape(p1, update=True)
    display.DisplayShape(p2, update=True)
    display.DisplayMessage(p1, "P1")
    display.DisplayMessage(p2, "P2")


if __name__ == "__main__":
    axs = gp_Ax3()

    ax0 = gp_Ax3(gp_Pnt(), gp_Dir(0, 0, 1), gp_Dir(1, 0, 0))
    pl0 = make_plane(ax0)
    show_axs_pln(ax0, scale=25, name="ax0")
    display.DisplayShape(pl0, color="RED", transparency=0.8)

    ax1 = gp_Ax3(gp_Pnt(100, 100, 0), gp_Dir(0, 0.5, 1), gp_Dir(1, 0, 0))
    pl1 = make_plane(ax1)
    show_axs_pln(ax1, scale=25, name="ax1")
    display.DisplayShape(pl1, color="BLUE1", transparency=0.8)
    
    display.View_Top()
    display.FitAll()
    display.View.Dump("./core_geometry_rotate_XY0.png")

    display.View_Rear()
    display.FitAll()
    display.View.Dump("./core_geometry_rotate_XZ0.png")

    display.View_Right()
    display.FitAll()
    display.View.Dump("./core_geometry_rotate_YZ0.png")
    
    ax0_1 = gp_Ax3(ax0.Location(), gp_Dir(0.0, 0.0, 1), gp_Dir(1, 0.5, 0))
    trf = gp_Trsf()
    trf.SetDisplacement(ax0_1, ax0)

    ax0.Transform(trf)
    pl0.Move(TopLoc_Location(trf))
    display.DisplayShape(pl0, color="RED", transparency=0.6)

    ax1.Transform(trf)
    pl1.Move(TopLoc_Location(trf))
    display.DisplayShape(pl1, color="BLUE1", transparency=0.6)

    display.View_Top()
    display.FitAll()
    display.View.Dump("./core_geometry_rotate_XY1.png")

    display.View_Rear()
    display.FitAll()
    display.View.Dump("./core_geometry_rotate_XZ1.png")

    display.View_Right()
    display.FitAll()
    display.View.Dump("./core_geometry_rotate_YZ1.png")
    
    start_display()
