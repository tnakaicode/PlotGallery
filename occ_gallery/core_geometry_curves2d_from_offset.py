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

import numpy as np
from OCC.Core.gp import gp_Pnt2d, gp_Vec2d, gp_Vec, gp_Pnt
from OCC.Core.TColgp import TColgp_Array1OfPnt2d, TColgp_HArray1OfPnt2d
from OCC.Core.GeomAbs import GeomAbs_Arc
from OCC.Core.Geom2dAPI import Geom2dAPI_PointsToBSpline, Geom2dAPI_Interpolate
from OCC.Core.Geom2d import Geom2d_OffsetCurve

from OCC.Display.SimpleGui import init_display

display, start_display, add_menu, add_function_to_menu = init_display()


def curves2d_from_offset(event=None):
    """
    @param display:
    """
    pnt2d_array = TColgp_Array1OfPnt2d(1, 5)
    pnt2d_array.SetValue(1, gp_Pnt2d(-4, 0))
    pnt2d_array.SetValue(2, gp_Pnt2d(-7, 2))
    pnt2d_array.SetValue(3, gp_Pnt2d(-6, 3))
    pnt2d_array.SetValue(4, gp_Pnt2d(-4, 3))
    pnt2d_array.SetValue(5, gp_Pnt2d(-3, 5))

    pnt2d_array_h = TColgp_HArray1OfPnt2d(1, 5)
    for i in range(pnt2d_array.Lower(), pnt2d_array.Upper() + 1):
        pnt2d_array_h.SetValue(i, pnt2d_array.Value(i))

    spline_1 = Geom2dAPI_PointsToBSpline(pnt2d_array).Curve()
    spline_2_api = Geom2dAPI_Interpolate(pnt2d_array_h, True, 0.1E-3)
    spline_2_api.Perform()
    spline_2 = spline_2_api.Curve()
    print(spline_2.Continuity(), spline_2.EndPoint())

    dist = 1
    offset_curve1 = Geom2d_OffsetCurve(spline_1, dist, True)
    result = offset_curve1.IsCN(2)
    print("Offset curve yellow is C2: %r" % result, offset_curve1.Continuity())
    dist2 = 0.1
    offset_curve2 = Geom2d_OffsetCurve(spline_2, dist2, True)
    result2 = offset_curve2.IsCN(2)
    print("Offset curve blue is C2: %r" % result2, offset_curve2.Continuity())

    # GeomAbs_C0 = 0
    # GeomAbs_G1 = 1
    # GeomAbs_C1 = 2
    # GeomAbs_G2 = 3
    # GeomAbs_C2 = 4
    # GeomAbs_C3 = 5
    # GeomAbs_CN = 6

    for u in np.linspace(spline_1.FirstParameter(), spline_1.LastParameter(), 11):
        p, v1, v2 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
        spline_1.D2(u, p, v1, v2)
        v2.Normalize()
        display.DisplayVector(gp_Vec(v2.X(), v2.Y(), 0),
                              gp_Pnt(p.X(), p.Y(), 0))

    for u in np.linspace(offset_curve2.FirstParameter(), offset_curve2.LastParameter(), 11):
        p, v1, v2 = gp_Pnt2d(), gp_Vec2d(), gp_Vec2d()
        offset_curve2.D2(u, p, v1, v2)
        v2.Normalize()
        display.DisplayShape(p)

    display.DisplayShape(spline_1)
    display.DisplayShape(spline_2)
    for i in range(pnt2d_array.Lower(), pnt2d_array.Upper() + 1):
        display.DisplayShape(pnt2d_array.Value(i))
    display.DisplayShape(offset_curve1, color="YELLOW")
    display.DisplayShape(offset_curve2, color="BLUE1", update=True)


if __name__ == "__main__":
    curves2d_from_offset()
    start_display()
